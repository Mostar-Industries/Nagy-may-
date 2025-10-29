// components/ui/mobile-workflow.tsx
'use client';

import { useState } from 'react';
// import { useSwipeable } from 'react-swipeable'; // not in package.json, commented out
// import { Camera } from '@/components/camera'; // component does not exist
// import { GeoLocation } from '@/components/geo-location'; // component does not exist

export function MobileWorkflow() {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    location: null,
    images: [],
    notes: '',
  });

  // const handlers = useSwipeable({
  //   onSwipedLeft: () => setStep(prev => Math.min(prev + 1, 4)),
  //   onSwipedRight: () => setStep(prev => Math.max(prev - 1, 1)),
  // });

  const handleSubmit = async () => {
    try {
      const response = await fetch('/api/field-reports', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      
      if (response.ok) {
        // Handle success
        setStep(1);
        // setFormData(...); // reset form data
        console.log('Field report submitted successfully');
      } else {
        console.error('Failed to submit field report');
      }
    } catch (error) {
      console.error('Error submitting field report:', error);
    }
  };

  return (
    <div>
      {/* Basic form for mobile workflow, swipe and camera functionality need to be implemented */}
      <h3>Step {step} of 4</h3>
      <input type="text" placeholder="Notes" onChange={(e) => setFormData({...formData, notes: e.target.value})} />
      <button onClick={handleSubmit}>Submit</button>
    </div>
  )
}
