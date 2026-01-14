// hooks/useRealtimeDetections.ts
// Subscribe to realtime rodent detections and plot on Cesium

import { useEffect, useRef } from 'react';
import { createClient } from '@supabase/supabase-js';
import { Viewer, Color, Cartesian3, VerticalOrigin, Cartesian2 } from 'cesium';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

interface Detection {
  id: string;
  detection_timestamp: string;
  source: string;
  latitude: number;
  longitude: number;
  detection_count: number;
  risk_assessment: {
    risk_score?: number;
    risk_level?: string;
    confidence?: number;
    detections?: Array<{
      species?: string;
      confidence?: number;
      bbox?: number[];
    }>;
    factors?: string[];
  };
}

export function useRealtimeDetections(viewer: Viewer | null) {
  const entitiesRef = useRef<Map<string, any>>(new Map());

  useEffect(() => {
    if (!viewer) return;

    // Load recent detections (last 24h)
    loadRecentDetections(viewer);

    // Subscribe to new detections
    const subscription = supabase
      .channel('detection_patterns')
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'detection_patterns',
        },
        (payload) => {
          const detection = payload.new as Detection;
          plotDetection(viewer, detection);
        }
      )
      .subscribe();

    return () => {
      subscription.unsubscribe();
    };
  }, [viewer]);

  async function loadRecentDetections(viewer: Viewer) {
    const { data } = await supabase
      .from('detection_patterns')
      .select('*')
      .gte('detection_timestamp', new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString())
      .order('detection_timestamp', { ascending: false });

    data?.forEach((detection: Detection) => {
      plotDetection(viewer, detection);
    });
  }

  function plotDetection(viewer: Viewer, detection: Detection) {
    if (!detection.latitude || !detection.longitude) return;

    const { latitude, longitude, risk_assessment, detection_count, source } = detection;
    const riskLevel = (risk_assessment?.risk_level || 'low').toLowerCase();

    // Risk color mapping
    const color = 
      riskLevel === 'high' ? Color.RED :
      riskLevel === 'medium' ? Color.ORANGE :
      Color.YELLOW;

    // Add point entity
    const entity = viewer.entities.add({
      id: detection.id,
      position: Cartesian3.fromDegrees(longitude, latitude, 0),
      point: {
        pixelSize: 15,
        color: color,
        outlineColor: Color.WHITE,
        outlineWidth: 2,
      },
      label: {
        text: `${detection_count || 0} Mastomys\n${riskLevel.toUpperCase()}`,
        font: '14px sans-serif',
        fillColor: Color.WHITE,
        outlineColor: Color.BLACK,
        outlineWidth: 2,
        verticalOrigin: VerticalOrigin.BOTTOM,
        pixelOffset: new Cartesian2(0, -15),
        showBackground: true,
        backgroundColor: color.withAlpha(0.7),
      },
      description: formatDescription(detection),
    });

    entitiesRef.current.set(detection.id, entity);

    // Auto-fly to new detections (high risk only)
    if (riskLevel === 'high') {
      viewer.flyTo(entity, {
        duration: 2,
        offset: {
          heading: 0,
          pitch: -45 * Math.PI / 180,
          range: 500,
        },
      });
    }
  }

  function formatDescription(detection: Detection): string {
    const { risk_assessment, source, detection_timestamp } = detection;
    const detections = risk_assessment?.detections || [];
    const riskLevel = (risk_assessment?.risk_level || 'low').toLowerCase();
    
    return `
      <div style="font-family: sans-serif;">
        <h3>Rodent Detection Alert</h3>
        <p><strong>Source:</strong> ${source}</p>
        <p><strong>Time:</strong> ${new Date(detection_timestamp).toLocaleString()}</p>
        <p><strong>Count:</strong> ${detections.length} rodents</p>
        
        <h4>Species Detected:</h4>
        <ul>
          ${detections.map(d => `
            <li>${d.species || 'Unknown'} - ${((d.confidence || 0) * 100).toFixed(1)}% confidence</li>
          `).join('')}
        </ul>
        
        <h4>Lassa Fever Risk:</h4>
        <p style="color: ${riskLevel === 'high' ? 'red' : 'orange'};">
          <strong>${riskLevel.toUpperCase()}</strong> (Score: ${(risk_assessment?.risk_score || 0).toFixed(2)})
        </p>
        
        ${Array.isArray(risk_assessment?.factors) && risk_assessment?.factors.length > 0 ? `
          <h4>Risk Factors:</h4>
          <ul>
            ${risk_assessment?.factors.map(f => `<li>${f}</li>`).join('')}
          </ul>
        ` : ''}
      </div>
    `;
  }
  return {
    entities: entitiesRef.current,
    clearDetections: () => {
      viewer?.entities.removeAll();
      entitiesRef.current.clear();
    },
  };
}
