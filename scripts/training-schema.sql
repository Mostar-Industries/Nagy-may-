-- Training System Schema for ML Model Training & Evaluation
-- Run this after enhanced-detections-schema.sql

-- Training sessions table
CREATE TABLE IF NOT EXISTS training_sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_name VARCHAR(255) NOT NULL,
  model_type VARCHAR(100) NOT NULL, -- yolov8n, yolov8s, yolov8m, etc.
  dataset_name VARCHAR(255),
  dataset_size INTEGER,
  epochs INTEGER NOT NULL,
  batch_size INTEGER NOT NULL,
  learning_rate DECIMAL(10, 8),
  img_size INTEGER DEFAULT 640,
  status VARCHAR(50) DEFAULT 'pending', -- pending, running, completed, failed, cancelled
  started_at TIMESTAMP WITH TIME ZONE,
  completed_at TIMESTAMP WITH TIME ZONE,
  duration_seconds INTEGER,
  best_epoch INTEGER,
  final_map50 DECIMAL(5, 4), -- mAP@0.5
  final_map50_95 DECIMAL(5, 4), -- mAP@0.5:0.95
  final_precision DECIMAL(5, 4),
  final_recall DECIMAL(5, 4),
  final_loss DECIMAL(10, 6),
  model_path TEXT,
  config JSONB DEFAULT '{}'::jsonb,
  hardware_info JSONB,
  created_by VARCHAR(100),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Training metrics (per epoch)
CREATE TABLE IF NOT EXISTS training_metrics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id UUID NOT NULL REFERENCES training_sessions(id) ON DELETE CASCADE,
  epoch INTEGER NOT NULL,
  box_loss DECIMAL(10, 6),
  cls_loss DECIMAL(10, 6),
  dfl_loss DECIMAL(10, 6),
  total_loss DECIMAL(10, 6),
  precision DECIMAL(5, 4),
  recall DECIMAL(5, 4),
  map50 DECIMAL(5, 4),
  map50_95 DECIMAL(5, 4),
  learning_rate DECIMAL(10, 8),
  epoch_time_seconds INTEGER,
  gpu_memory_mb INTEGER,
  recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(session_id, epoch)
);

-- Validation results
CREATE TABLE IF NOT EXISTS validation_results (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id UUID NOT NULL REFERENCES training_sessions(id) ON DELETE CASCADE,
  validation_set VARCHAR(100) NOT NULL, -- train, val, test
  epoch INTEGER,
  class_name VARCHAR(100),
  images_count INTEGER,
  instances_count INTEGER,
  precision DECIMAL(5, 4),
  recall DECIMAL(5, 4),
  map50 DECIMAL(5, 4),
  map50_95 DECIMAL(5, 4),
  confusion_matrix JSONB,
  recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Model inference benchmarks
CREATE TABLE IF NOT EXISTS model_benchmarks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id UUID REFERENCES training_sessions(id) ON DELETE SET NULL,
  model_name VARCHAR(255) NOT NULL,
  model_size_mb DECIMAL(10, 2),
  device VARCHAR(50) NOT NULL, -- cpu, cuda, mps
  avg_inference_ms DECIMAL(10, 2),
  min_inference_ms DECIMAL(10, 2),
  max_inference_ms DECIMAL(10, 2),
  throughput_fps DECIMAL(10, 2),
  batch_size INTEGER DEFAULT 1,
  image_size INTEGER DEFAULT 640,
  test_images_count INTEGER,
  hardware_info JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Dataset statistics
CREATE TABLE IF NOT EXISTS training_datasets (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  dataset_name VARCHAR(255) UNIQUE NOT NULL,
  description TEXT,
  total_images INTEGER,
  train_split INTEGER,
  val_split INTEGER,
  test_split INTEGER,
  class_distribution JSONB,
  annotation_format VARCHAR(50), -- yolo, coco, voc
  image_size_stats JSONB,
  storage_path TEXT,
  version VARCHAR(50),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Hyperparameter tuning history
CREATE TABLE IF NOT EXISTS hyperparameter_runs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  experiment_name VARCHAR(255) NOT NULL,
  session_id UUID REFERENCES training_sessions(id) ON DELETE CASCADE,
  hyperparameters JSONB NOT NULL,
  metrics JSONB,
  score DECIMAL(10, 6),
  rank INTEGER,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_training_sessions_status ON training_sessions(status);
CREATE INDEX IF NOT EXISTS idx_training_sessions_created ON training_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_training_sessions_model_type ON training_sessions(model_type);
CREATE INDEX IF NOT EXISTS idx_training_metrics_session ON training_metrics(session_id, epoch);
CREATE INDEX IF NOT EXISTS idx_validation_results_session ON validation_results(session_id);
CREATE INDEX IF NOT EXISTS idx_model_benchmarks_model ON model_benchmarks(model_name);
CREATE INDEX IF NOT EXISTS idx_training_datasets_name ON training_datasets(dataset_name);
CREATE INDEX IF NOT EXISTS idx_hyperparameter_runs_experiment ON hyperparameter_runs(experiment_name);

-- Real-time training metrics view
CREATE OR REPLACE VIEW active_training_sessions AS
SELECT 
  ts.id,
  ts.session_name,
  ts.model_type,
  ts.status,
  ts.epochs,
  ts.started_at,
  ts.duration_seconds,
  ts.final_map50,
  ts.final_map50_95,
  COUNT(tm.id) as completed_epochs,
  MAX(tm.epoch) as current_epoch,
  AVG(tm.total_loss) as avg_loss,
  MAX(tm.map50) as best_map50,
  ARRAY_AGG(
    jsonb_build_object(
      'epoch', tm.epoch,
      'loss', tm.total_loss,
      'map50', tm.map50,
      'precision', tm.precision,
      'recall', tm.recall
    ) ORDER BY tm.epoch DESC
  ) FILTER (WHERE tm.epoch IS NOT NULL) as recent_metrics
FROM training_sessions ts
LEFT JOIN training_metrics tm ON ts.id = tm.session_id
WHERE ts.status IN ('running', 'pending')
GROUP BY ts.id, ts.session_name, ts.model_type, ts.status, ts.epochs, 
         ts.started_at, ts.duration_seconds, ts.final_map50, ts.final_map50_95
ORDER BY ts.started_at DESC;

-- Training performance summary
CREATE OR REPLACE VIEW training_performance_summary AS
SELECT 
  ts.id,
  ts.session_name,
  ts.model_type,
  ts.dataset_name,
  ts.status,
  ts.epochs,
  ts.final_map50,
  ts.final_map50_95,
  ts.final_precision,
  ts.final_recall,
  ts.duration_seconds,
  ts.created_at,
  (
    SELECT jsonb_agg(
      jsonb_build_object(
        'epoch', epoch,
        'total_loss', total_loss,
        'map50', map50,
        'map50_95', map50_95,
        'precision', precision,
        'recall', recall
      ) ORDER BY epoch
    )
    FROM training_metrics 
    WHERE session_id = ts.id
  ) as epoch_metrics,
  (
    SELECT jsonb_agg(
      jsonb_build_object(
        'class', class_name,
        'precision', precision,
        'recall', recall,
        'map50', map50
      )
    )
    FROM validation_results 
    WHERE session_id = ts.id AND validation_set = 'val'
  ) as class_metrics
FROM training_sessions ts
ORDER BY ts.created_at DESC;

-- Best models leaderboard
CREATE OR REPLACE VIEW models_leaderboard AS
SELECT 
  ts.id,
  ts.session_name,
  ts.model_type,
  ts.dataset_name,
  ts.final_map50,
  ts.final_map50_95,
  ts.final_precision,
  ts.final_recall,
  ts.epochs,
  ts.duration_seconds,
  mb.avg_inference_ms,
  mb.throughput_fps,
  ts.created_at,
  ROW_NUMBER() OVER (ORDER BY ts.final_map50_95 DESC) as rank
FROM training_sessions ts
LEFT JOIN model_benchmarks mb ON ts.id = mb.session_id
WHERE ts.status = 'completed' AND ts.final_map50_95 IS NOT NULL
ORDER BY ts.final_map50_95 DESC
LIMIT 50;

-- Function to update session status and metrics
CREATE OR REPLACE FUNCTION update_training_session()
RETURNS TRIGGER AS $$
BEGIN
  -- Auto-calculate best epoch and duration
  IF NEW.status = 'completed' THEN
    -- Get best epoch based on mAP50-95
    SELECT epoch INTO NEW.best_epoch
    FROM training_metrics
    WHERE session_id = NEW.id
    ORDER BY map50_95 DESC NULLS LAST
    LIMIT 1;
    
    -- Calculate duration if not set
    IF NEW.duration_seconds IS NULL AND NEW.started_at IS NOT NULL AND NEW.completed_at IS NOT NULL THEN
      NEW.duration_seconds = EXTRACT(EPOCH FROM (NEW.completed_at - NEW.started_at))::INTEGER;
    END IF;
  END IF;
  
  -- Update timestamp
  NEW.updated_at = NOW();
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_training_session
  BEFORE UPDATE ON training_sessions
  FOR EACH ROW
  EXECUTE FUNCTION update_training_session();

-- Function to calculate average metrics
CREATE OR REPLACE FUNCTION get_session_avg_metrics(p_session_id UUID)
RETURNS TABLE(
  avg_loss DECIMAL,
  avg_map50 DECIMAL,
  avg_precision DECIMAL,
  avg_recall DECIMAL,
  improvement_rate DECIMAL
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    AVG(total_loss)::DECIMAL(10,6) as avg_loss,
    AVG(map50)::DECIMAL(5,4) as avg_map50,
    AVG(precision)::DECIMAL(5,4) as avg_precision,
    AVG(recall)::DECIMAL(5,4) as avg_recall,
    (
      (MAX(map50) - MIN(map50)) / NULLIF(MAX(epoch) - MIN(epoch), 0)
    )::DECIMAL(10,6) as improvement_rate
  FROM training_metrics
  WHERE session_id = p_session_id;
END;
$$ LANGUAGE plpgsql;

-- Comments
COMMENT ON TABLE training_sessions IS 'ML model training sessions with configuration and results';
COMMENT ON TABLE training_metrics IS 'Per-epoch training metrics (loss, mAP, precision, recall)';
COMMENT ON TABLE validation_results IS 'Validation results per class and dataset split';
COMMENT ON TABLE model_benchmarks IS 'Inference speed benchmarks for trained models';
COMMENT ON TABLE training_datasets IS 'Dataset metadata and statistics';
COMMENT ON TABLE hyperparameter_runs IS 'Hyperparameter tuning experiments';
COMMENT ON VIEW active_training_sessions IS 'Real-time view of currently running training sessions';
COMMENT ON VIEW models_leaderboard IS 'Top performing models ranked by mAP50-95';

-- Grant permissions (uncomment and adjust as needed)
-- GRANT SELECT, INSERT, UPDATE ON training_sessions TO your_app_user;
-- GRANT SELECT, INSERT ON training_metrics TO your_app_user;
-- GRANT SELECT, INSERT ON validation_results TO your_app_user;
-- GRANT SELECT, INSERT ON model_benchmarks TO your_app_user;
-- GRANT SELECT ON active_training_sessions TO your_app_user;
-- GRANT SELECT ON models_leaderboard TO your_app_user;
