import * as tf from '@tensorflow/tfjs';

// Create a model with the specific columns provided
const createModel = () => {
  const model = tf.sequential();
  
  // Calculate total number of features based on actual data categories
  const categoryOptions = ['Mobile Phone', 'Computer', 'Television', 'Large Home Appliance', 'Automotive', 'Miscellaneous'];
  const subcategoryOptions = ['Tablet', 'Tablet PC', 'LCD TV', 'Laptop', 'Processor', 'Refrigerator', 'Electronic', 'Car Battery', 'LED Monitor'];
  const brandOptions = ['Lenovo', 'Apple', 'Samsung', 'HP', 'Intel', 'LG', 'Mettler', 'Bosch', 'Logitech'];
  const conditionOptions = ['Working', 'Dead', 'Faulty'];
  const materialOptions = ['Metal', 'Aluminum', 'Plastic', 'Copper', 'Lithium'];
  const locationOptions = ['New Delhi', 'Delhi', 'Karnataka', 'Kerala', 'Andhra Pradesh', 'Chennai', 'Bangalore', 'GOA'];
  
  const FEATURE_SIZE = 
    categoryOptions.length +
    subcategoryOptions.length +
    brandOptions.length +
    conditionOptions.length +
    materialOptions.length +
    locationOptions.length +
    4; // age_years, weight_kg, original_price, demand_supply_index
  
  // Input layer with regularization
  model.add(tf.layers.dense({
    inputShape: [FEATURE_SIZE],
    units: 64,
    kernelInitializer: 'glorotNormal',
    kernelRegularizer: tf.regularizers.l1l2({ l1: 0.01, l2: 0.01 })
  }));
  model.add(tf.layers.batchNormalization());
  model.add(tf.layers.activation({ activation: 'relu' }));
  model.add(tf.layers.dropout({ rate: 0.2 }));
  
  // Hidden layer with regularization
  model.add(tf.layers.dense({
    units: 32,
    kernelInitializer: 'glorotNormal',
    kernelRegularizer: tf.regularizers.l1l2({ l1: 0.01, l2: 0.01 })
  }));
  model.add(tf.layers.batchNormalization());
  model.add(tf.layers.activation({ activation: 'relu' }));
  model.add(tf.layers.dropout({ rate: 0.1 }));
  
  // Output layer
  model.add(tf.layers.dense({
    units: 1,
    activation: 'relu' // Ensure non-negative predictions
  }));
  
  // Compile with Huber loss for robustness against outliers
  model.compile({
    optimizer: tf.train.adam(0.001),
    loss: tf.losses.huberLoss,
    metrics: ['mse']
  });
  
  return model;
};

// Function to encode categorical features
const encodeCategoricalFeatures = (data) => {
  // Define possible values for each categorical feature based on actual data
  const categoryOptions = ['Mobile Phone', 'Computer', 'Television', 'Large Home Appliance', 'Automotive', 'Miscellaneous'];
  const subcategoryOptions = ['Tablet', 'Tablet PC', 'LCD TV', 'Laptop', 'Processor', 'Refrigerator', 'Electronic', 'Car Battery', 'LED Monitor'];
  const brandOptions = ['Lenovo', 'Apple', 'Samsung', 'HP', 'Intel', 'LG', 'Mettler', 'Bosch', 'Logitech'];
  const conditionOptions = ['Working', 'Dead', 'Faulty'];
  const materialOptions = ['Metal', 'Aluminum', 'Plastic', 'Copper', 'Lithium'];
  const locationOptions = ['New Delhi', 'Delhi', 'Karnataka', 'Kerala', 'Andhra Pradesh', 'Chennai', 'Bangalore', 'GOA'];
  
  // One-hot encode each categorical feature
  const categoryEncoded = Array(categoryOptions.length).fill(0);
  const subcategoryEncoded = Array(subcategoryOptions.length).fill(0);
  const brandEncoded = Array(brandOptions.length).fill(0);
  const conditionEncoded = Array(conditionOptions.length).fill(0);
  const materialEncoded = Array(materialOptions.length).fill(0);
  const locationEncoded = Array(locationOptions.length).fill(0);
  
  // Helper function to find closest match for categories
  const findClosestMatch = (value, options) => {
    if (!value) return -1;
    const normalizedValue = value.toLowerCase().trim();
    return options.findIndex(opt => 
      normalizedValue.includes(opt.toLowerCase()) || 
      opt.toLowerCase().includes(normalizedValue)
    );
  };
  
  // Set the appropriate index to 1 for each feature
  const categoryIndex = findClosestMatch(data.category, categoryOptions);
  if (categoryIndex !== -1) categoryEncoded[categoryIndex] = 1;
  
  const subcategoryIndex = findClosestMatch(data.subcategory, subcategoryOptions);
  if (subcategoryIndex !== -1) subcategoryEncoded[subcategoryIndex] = 1;
  
  const brandIndex = findClosestMatch(data.brand, brandOptions);
  if (brandIndex !== -1) brandEncoded[brandIndex] = 1;
  
  const conditionIndex = findClosestMatch(data.condition, conditionOptions);
  if (conditionIndex !== -1) conditionEncoded[conditionIndex] = 1;
  
  const materialIndex = findClosestMatch(data.scrap_material, materialOptions);
  if (materialIndex !== -1) materialEncoded[materialIndex] = 1;
  
  const locationIndex = findClosestMatch(data.location, locationOptions);
  if (locationIndex !== -1) locationEncoded[locationIndex] = 1;
  
  // Normalize numerical features based on the example data ranges
  const ageNormalized = data.age_years / 15; // Normalize age (max observed is around 12.7 years)
  const weightNormalized = data.weight_kg / 120; // Normalize weight (max observed is around 119 kg)
  const originalPriceNormalized = data.original_price / 60000; // Normalize price (max observed is around 54600)
  
  // Combine all features into a single array
  return [
    ...categoryEncoded,
    ...subcategoryEncoded,
    ...brandEncoded,
    ...conditionEncoded,
    ...materialEncoded,
    ...locationEncoded,
    ageNormalized,
    weightNormalized,
    originalPriceNormalized,
    data.demand_supply_index
  ];
};

// Function to preprocess training data
const preprocessTrainingData = (rawData) => {
  const features = rawData.map(item => encodeCategoricalFeatures(item));
  const labels = rawData.map(item => item.estimated_price);
  
  // Calculate statistics for feature normalization
  const featureMeans = [];
  const featureStds = [];
  
  // Normalize each feature
  for (let i = 0; i < features[0].length; i++) {
    const featureValues = features.map(f => f[i]);
    const mean = featureValues.reduce((a, b) => a + b, 0) / featureValues.length;
    const std = Math.sqrt(featureValues.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / featureValues.length);
    
    featureMeans.push(mean);
    featureStds.push(std);
    
    // Normalize the feature
    features.forEach(f => {
      f[i] = (f[i] - mean) / (std + 1e-8);
    });
  }
  
  // Calculate statistics for label normalization
  const labelMean = labels.reduce((a, b) => a + b, 0) / labels.length;
  const labelStd = Math.sqrt(labels.reduce((a, b) => a + Math.pow(b - labelMean, 2), 0) / labels.length);
  
  // Normalize labels
  const normalizedLabels = labels.map(price => (price - labelMean) / (labelStd + 1e-8));
  
  return {
    features,
    labels: normalizedLabels,
    featureMeans,
    featureStds,
    labelMean,
    labelStd
  };
};

// Function to calculate evaluation metrics
const calculateMetrics = (actual, predicted) => {
  const actualMean = actual.reduce((sum, val) => sum + val, 0) / actual.length;
  
  // Calculate MAE (Mean Absolute Error)
  const mae = actual.reduce((sum, val, i) => sum + Math.abs(val - predicted[i]), 0) / actual.length;
  
  // Calculate RMSE (Root Mean Square Error)
  const mse = actual.reduce((sum, val, i) => sum + Math.pow(val - predicted[i], 2), 0) / actual.length;
  const rmse = Math.sqrt(mse);
  
  // Calculate R² (R-squared)
  const totalSumSquares = actual.reduce((sum, val) => sum + Math.pow(val - actualMean, 2), 0);
  const residualSumSquares = actual.reduce((sum, val, i) => sum + Math.pow(val - predicted[i], 2), 0);
  const rSquared = 1 - (residualSumSquares / totalSumSquares);
  
  // Calculate MAPE (Mean Absolute Percentage Error)
  const mape = actual.reduce((sum, val, i) => {
    return sum + Math.abs((val - predicted[i]) / val);
  }, 0) / actual.length * 100;
  
  return {
    mae,
    rmse,
    rSquared,
    mape
  };
};

// Function to calculate accuracy metrics
const calculateAccuracyMetrics = (actual, predicted) => {
  // Calculate basic accuracy metrics
  const errors = actual.map((val, i) => Math.abs(val - predicted[i]));
  const percentErrors = actual.map((val, i) => Math.abs((val - predicted[i]) / val) * 100);
  
  // Calculate accuracy within different thresholds
  const within10Percent = percentErrors.filter(err => err <= 10).length / actual.length * 100;
  const within20Percent = percentErrors.filter(err => err <= 20).length / actual.length * 100;
  const within50Percent = percentErrors.filter(err => err <= 50).length / actual.length * 100;
  
  // Calculate price range based accuracy
  const priceRanges = [
    { min: 0, max: 1000, count: 0, correct: 0 },
    { min: 1000, max: 5000, count: 0, correct: 0 },
    { min: 5000, max: 10000, count: 0, correct: 0 },
    { min: 10000, max: Infinity, count: 0, correct: 0 }
  ];
  
  actual.forEach((val, i) => {
    const range = priceRanges.find(r => val >= r.min && val < r.max);
    if (range) {
      range.count++;
      if (percentErrors[i] <= 20) { // Consider prediction correct if within 20%
        range.correct++;
      }
    }
  });
  
  // Calculate accuracy for each price range
  const rangeAccuracy = priceRanges.map(range => ({
    range: `₹${range.min}-${range.max === Infinity ? '∞' : range.max}`,
    accuracy: range.count > 0 ? (range.correct / range.count * 100) : 0,
    samples: range.count
  }));
  
  return {
    accuracyWithin10Percent: within10Percent,
    accuracyWithin20Percent: within20Percent,
    accuracyWithin50Percent: within50Percent,
    priceRangeAccuracy: rangeAccuracy,
    meanPercentageError: percentErrors.reduce((a, b) => a + b, 0) / percentErrors.length
  };
};

// Function to create confusion matrix for price ranges
const createConfusionMatrix = (actual, predicted) => {
  const ranges = [
    { label: '0-1k', min: 0, max: 1000 },
    { label: '1k-5k', min: 1000, max: 5000 },
    { label: '5k-10k', min: 5000, max: 10000 },
    { label: '10k+', min: 10000, max: Infinity }
  ];
  
  // Initialize confusion matrix
  const matrix = Array(ranges.length).fill(0).map(() => Array(ranges.length).fill(0));
  
  // Fill confusion matrix
  actual.forEach((actualVal, i) => {
    const predictedVal = predicted[i];
    const actualRangeIndex = ranges.findIndex(r => actualVal >= r.min && actualVal < r.max);
    const predictedRangeIndex = ranges.findIndex(r => predictedVal >= r.min && predictedVal < r.max);
    if (actualRangeIndex !== -1 && predictedRangeIndex !== -1) {
      matrix[actualRangeIndex][predictedRangeIndex]++;
    }
  });
  
  return {
    matrix,
    labels: ranges.map(r => r.label)
  };
};

// Modified evaluate function to include new metrics
const evaluateModel = async (model, features, labels) => {
  const predictions = [];
  const batchSize = 32;
  
  // Make predictions in batches
  for (let i = 0; i < features.length; i += batchSize) {
    const batchFeatures = features.slice(i, i + batchSize);
    const featureTensor = tf.tensor2d(batchFeatures);
    const predictionTensor = model.predict(featureTensor);
    const batchPredictions = await predictionTensor.data();
    predictions.push(...batchPredictions);
    
    featureTensor.dispose();
    predictionTensor.dispose();
  }
  
  // Calculate all metrics
  const actualValues = labels.map(l => l[0]);
  const basicMetrics = calculateMetrics(actualValues, predictions);
  const accuracyMetrics = calculateAccuracyMetrics(actualValues, predictions);
  const confusionMatrix = createConfusionMatrix(actualValues, predictions);
  
  // Print detailed evaluation results
  console.log('\n=== Model Evaluation Results ===');
  console.log('\nBasic Metrics:');
  console.log(`MAE: ₹${basicMetrics.mae.toFixed(2)}`);
  console.log(`RMSE: ₹${basicMetrics.rmse.toFixed(2)}`);
  console.log(`R² Score: ${(basicMetrics.rSquared * 100).toFixed(2)}%`);
  console.log(`MAPE: ${basicMetrics.mape.toFixed(2)}%`);
  
  console.log('\nAccuracy Metrics:');
  console.log(`Predictions within 10% of actual: ${accuracyMetrics.accuracyWithin10Percent.toFixed(2)}%`);
  console.log(`Predictions within 20% of actual: ${accuracyMetrics.accuracyWithin20Percent.toFixed(2)}%`);
  console.log(`Predictions within 50% of actual: ${accuracyMetrics.accuracyWithin50Percent.toFixed(2)}%`);
  console.log(`Mean Percentage Error: ${accuracyMetrics.meanPercentageError.toFixed(2)}%`);
  
  console.log('\nPrice Range Accuracy:');
  accuracyMetrics.priceRangeAccuracy.forEach(range => {
    console.log(`${range.range}: ${range.accuracy.toFixed(2)}% (${range.samples} samples)`);
  });
  
  console.log('\nConfusion Matrix:');
  console.log('Predicted →');
  console.log('Actual ↓');
  console.log('    ' + confusionMatrix.labels.join('   '));
  confusionMatrix.matrix.forEach((row, i) => {
    console.log(`${confusionMatrix.labels[i]} ${row.map(v => v.toString().padStart(4)).join(' ')}`);
  });
  
  return {
    predictions,
    metrics: {
      ...basicMetrics,
      ...accuracyMetrics,
      confusionMatrix
    }
  };
};

// Modified train function with improved configuration
const trainModel = async (model, preprocessedData) => {
  const { features, labels, featureMeans, featureStds, labelMean, labelStd } = preprocessedData;
  
  // Split data into training (80%) and validation (20%) sets
  const splitIndex = Math.floor(features.length * 0.8);
  const trainFeatures = features.slice(0, splitIndex);
  const trainLabels = labels.slice(0, splitIndex);
  const valFeatures = features.slice(splitIndex);
  const valLabels = labels.slice(splitIndex);
  
  // Convert features and labels to tensors
  const featureTensor = tf.tensor2d(trainFeatures);
  const labelTensor = tf.tensor2d(trainLabels.map(l => [l]));
  const valFeatureTensor = tf.tensor2d(valFeatures);
  const valLabelTensor = tf.tensor2d(valLabels.map(l => [l]));
  
  try {
    console.log('\n=== Starting Model Training ===');
    console.log(`Training samples: ${trainFeatures.length}`);
    console.log(`Validation samples: ${valFeatures.length}`);
    
    // Create callbacks for monitoring training
    const earlyStopping = tf.callbacks.earlyStopping({
      monitor: 'val_loss',
      minDelta: 1e-4,
      patience: 15,
      verbose: 1,
      mode: 'min',
      restoreBestModel: true
    });
    
    class LoggingCallback extends tf.Callback {
      onEpochEnd(epoch, logs) {
        if (epoch % 5 === 0) {
          console.log(`Epoch ${epoch}: loss = ${logs.loss.toFixed(4)}, val_loss = ${logs.val_loss.toFixed(4)}`);
        }
      }
    }
    
    // Train the model with improved configuration
    const history = await model.fit(featureTensor, labelTensor, {
      epochs: 200,
      batchSize: 16,
      validationData: [valFeatureTensor, valLabelTensor],
      verbose: 0,
      callbacks: [earlyStopping, new LoggingCallback()],
      shuffle: true
    });
    
    console.log('\n=== Training Complete ===');
    
    // Evaluate model on validation set
    console.log('\n=== Validation Set Evaluation ===');
    const evalResult = await evaluateModel(model, valFeatures, valLabels.map(l => [l * labelStd + labelMean]));
    
    // Clean up tensors
    featureTensor.dispose();
    labelTensor.dispose();
    valFeatureTensor.dispose();
    valLabelTensor.dispose();
    
    return {
      history,
      validationMetrics: evalResult.metrics,
      normalization: {
        featureMeans,
        featureStds,
        labelMean,
        labelStd
      }
    };
  } catch (error) {
    // Clean up tensors in case of error
    featureTensor.dispose();
    labelTensor.dispose();
    valFeatureTensor.dispose();
    valLabelTensor.dispose();
    throw error;
  }
};

// Modified predict function to handle feature normalization
const predictPrice = (model, inputFeatures, normalization) => {
  // Normalize input features
  const normalizedFeatures = inputFeatures.map((feature, i) => 
    (feature - normalization.featureMeans[i]) / (normalization.featureStds[i] + 1e-8)
  );
  
  const featureTensor = tf.tensor2d([normalizedFeatures], [1, normalizedFeatures.length]);
  try {
    const normalizedPrediction = model.predict(featureTensor);
    const prediction = normalizedPrediction.dataSync()[0] * normalization.labelStd + normalization.labelMean;
    return prediction;
  } finally {
    featureTensor.dispose();
  }
};

// Save model to browser local storage
const saveModel = async (model) => {
  await model.save('localstorage://ewaste-price-model');
  console.log('Model saved to local storage');
};

// Load model from browser local storage
const loadModel = async () => {
  try {
    const model = await tf.loadLayersModel('localstorage://ewaste-price-model');
    // Ensure model is compiled after loading
    model.compile({
      optimizer: tf.train.adam(0.001),
      loss: 'meanSquaredError',
      metrics: ['mse']
    });
    console.log('Model loaded from local storage and compiled');
    return model;
  } catch (error) {
    console.log('No saved model found, creating new model');
    const model = createModel(); // createModel already includes compilation
    return model;
  }
};

export { 
  createModel, 
  encodeCategoricalFeatures, 
  preprocessTrainingData, 
  trainModel, 
  predictPrice,
  saveModel,
  loadModel,
  evaluateModel
};
