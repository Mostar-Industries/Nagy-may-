// lib/analytics/predictive-model.ts
import * as tf from '@tensorflow/tfjs';

export async function trainPredictiveModel(historicalData: any[]) {
  // Prepare data
  const xs = historicalData.map(d => [
    d.temperature, 
    d.humidity, 
    d.rainfall, 
    d.population_density
  ]);
  
  const ys = historicalData.map(d => d.case_count);
  
  // Create and train model
  const model = tf.sequential();
  model.add(tf.layers.dense({units: 10, activation: 'relu', inputShape: [4]}));
  model.add(tf.layers.dense({units: 1}));
  
  model.compile({
    optimizer: 'adam',
    loss: 'meanSquaredError'
  });
  
  const xsTensor = tf.tensor2d(xs);
  const ysTensor = tf.tensor1d(ys);
  
  await model.fit(xsTensor, ysTensor, {
    epochs: 100,
    callbacks: {
      onEpochEnd: (epoch, logs) => {
        console.log(`Epoch ${epoch}: loss = ${logs?.loss}`);
      }
    }
  });
  
  // Save model
  await model.save('localstorage://mastomys-prediction-model');
  
  return model;
}
