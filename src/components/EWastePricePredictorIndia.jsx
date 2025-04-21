import React, { useState, useEffect } from 'react';
import { 
  createModel, 
  encodeCategoricalFeatures, 
  preprocessTrainingData, 
  trainModel, 
  predictPrice,
  saveModel,
  loadModel
} from "../model";
import { loadCSVData, prepareTrainingData, saveTrainingData, loadTrainingData } from "../csvLoader";
import PriceFactorVisualization from "./PriceFactorVisualization";

const ComboBox = ({ value, onChange, options, placeholder, className }) => {
  const [isCustom, setIsCustom] = useState(false);
  const [customValue, setCustomValue] = useState('');

  useEffect(() => {
    if (!options.includes(value) && value) {
      setIsCustom(true);
      setCustomValue(value);
    }
  }, [value, options]);

  const handleSelectChange = (e) => {
    const selectedValue = e.target.value;
    if (selectedValue === 'custom') {
      setIsCustom(true);
      onChange(customValue);
    } else {
      setIsCustom(false);
      onChange(selectedValue);
    }
  };

  const handleCustomInputChange = (e) => {
    const newValue = e.target.value;
    setCustomValue(newValue);
    onChange(newValue);
  };

  return (
    <div className="flex flex-col gap-2">
      <select
        value={isCustom ? 'custom' : value}
        onChange={handleSelectChange}
        className={`p-2 bg-gray-800 border border-gray-700 rounded text-gray-200 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 ${className}`}
      >
        <option value="">Select {placeholder}</option>
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
        <option value="custom">Enter Custom {placeholder}</option>
      </select>
      {isCustom && (
        <input
          type="text"
          value={customValue}
          onChange={handleCustomInputChange}
          placeholder={`Enter custom ${placeholder.toLowerCase()}`}
          className="p-2 bg-gray-800 border border-gray-700 rounded text-gray-200 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
        />
      )}
    </div>
  );
};

const EWastePricePredictorIndia = () => {
  const [model, setModel] = useState(null);
  const [normalization, setNormalization] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isTraining, setIsTraining] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [trainingData, setTrainingData] = useState(null);
  const [modelTrained, setModelTrained] = useState(false);
  const [csvUploadError, setCsvUploadError] = useState(null);
  
  const [formData, setFormData] = useState({
    category: '',
    subcategory: '',
    brand: '',
    model: '',
    age_years: '',
    condition: '',
    weight_kg: '',
    original_price: '',
    scrap_material: '',
    location: '',
    demand_supply_index: ''
  });

  // Initialize the model and check for pre-trained data
  useEffect(() => {
    const init = async () => {
      try {
        // Try to load existing model from localStorage
        const loadedModel = await loadModel();
        setModel(loadedModel);
        
        // Check if we already have training data saved
        const savedTrainingData = loadTrainingData();
        if (savedTrainingData) {
          setTrainingData(savedTrainingData);
          setModelTrained(true);
        }
      } catch (error) {
        console.error("Error initializing:", error);
        // If no model exists, create a new one
        const newModel = createModel();
        setModel(newModel);
      } finally {
        setIsLoading(false);
      }
    };

    init();
  }, []);

  // Handle file upload
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    
    try {
      setCsvUploadError(null);
      setIsLoading(true);
      
      // Check file extension
      const fileExtension = file.name.split('.').pop().toLowerCase();
      if (!['csv', 'xlsx', 'xls'].includes(fileExtension)) {
        throw new Error('Please upload a CSV or Excel file (.csv, .xlsx, .xls)');
      }
      
      // Check file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        throw new Error('File size exceeds 10MB limit');
      }
      
      // Parse the file
      const data = await loadCSVData(file);
      
      if (!data || data.length === 0) {
        throw new Error('The file is empty or contains no valid data');
      }
      
      // Validate and prepare the data
      const cleanData = prepareTrainingData(data);
      
      if (!cleanData || cleanData.length === 0) {
        throw new Error('No valid data found after validation. Please check the required columns.');
      }
      
      // Save the data for future use
      saveTrainingData(cleanData);
      
      // Set the data for training
      setTrainingData(cleanData);
      setIsLoading(false);
      
      // Train the model automatically after data is loaded
      if (model && cleanData.length > 0) {
        await trainModelWithData(cleanData);
      }
    } catch (error) {
      console.error("Error loading file:", error);
      setCsvUploadError(error.message || "Failed to load file. Please check the file format and try again.");
      setIsLoading(false);
      
      // Reset the file input
      event.target.value = '';
    }
  };

  // Function to train the model with the provided data
  const trainModelWithData = async (data) => {
    try {
      const preprocessedData = preprocessTrainingData(data);
      const newModel = createModel();
      const result = await trainModel(newModel, preprocessedData);
      
      setModel(newModel);
      setNormalization(result.normalization);
      
      // Save model and normalization parameters
      await saveModel(newModel);
      localStorage.setItem('ewaste-normalization', JSON.stringify(result.normalization));
      
      console.log('Model trained successfully');
    } catch (error) {
      console.error('Error training model:', error);
      throw error;
    }
  };

  // Handle making a prediction
  const handlePredict = () => {
    if (!model || !modelTrained) {
      alert('Please upload CSV data and train the model first.');
      return;
    }
    
    try {
      const features = encodeCategoricalFeatures(formData);
      const predictedPrice = predictPrice(model, features, normalization);
      
      // Round to nearest 10 rupees for a more realistic price
      const roundedPrice = Math.round(predictedPrice / 10) * 10;
      
      setPrediction(roundedPrice);
    } catch (error) {
      console.error("Prediction error:", error);
      alert('Error making prediction. Please check the console for details.');
    }
  };

  // Handle form input changes
  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Function to download sample CSV template
  const downloadSampleTemplate = () => {
    const headers = [
      'category,subcategory,brand,model,age_years,condition,weight_kg,original_price,scrap_material,location,demand_supply_index,estimated_price'
    ];
    const sampleData = [
      'Laptop,Motherboard,Dell,Inspiron 15,3,Working,2.3,45000,Metal,Mumbai,0.7,12000',
      'Mobile,Battery,Samsung,Galaxy S10,2,Faulty,0.2,35000,Lithium,Delhi,0.8,5000',
      'TV,Screen,LG,Smart TV 4K,4,Working,8.5,55000,Plastic,Bangalore,0.6,15000'
    ];
    
    const csvContent = [...headers, ...sampleData].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', 'ewaste_price_template.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (isLoading) {
    return <div className="text-center p-8 text-blue-400">Loading model...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto p-6 bg-gray-900 rounded-lg shadow-xl border border-blue-900">
      <h1 className="text-3xl font-bold mb-6 text-center text-blue-400 bg-gradient-to-r from-blue-500 to-indigo-700 bg-clip-text text-transparent">E-Waste Price Predictor (Indian Market)</h1>
      
      {/* CSV Upload Section */}
      <div className="mb-8 p-4 border border-dashed border-gray-700 rounded-lg bg-gray-800">
        <h2 className="text-xl font-semibold mb-4 text-blue-300">Train Model with Data</h2>
        <div className="flex flex-col md:flex-row items-center gap-4">
          <div className="relative overflow-hidden">
            <input
              type="file"
              accept=".csv,.xlsx,.xls"
              onChange={handleFileUpload}
              className="bg-gray-800 border border-gray-700 rounded text-gray-300 p-2 cursor-pointer file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-800 file:text-white hover:file:bg-blue-700"
              disabled={isTraining}
            />
          </div>
          <div className="flex-1">
            {isTraining ? (
              <div className="text-blue-400">Training in progress...</div>
            ) : modelTrained ? (
              <div className="text-green-400">✓ Model trained with {trainingData?.length || 0} data points</div>
            ) : (
              <div className="text-gray-400">Upload your CSV or Excel file with e-waste pricing data</div>
            )}
            {csvUploadError && (
              <div className="text-red-400 mt-2 p-2 bg-red-900 bg-opacity-30 rounded border border-red-800">
                {csvUploadError}
              </div>
            )}
          </div>
        </div>
        
        <div className="mt-4 text-sm text-gray-400">
          <div className="flex justify-between items-center mb-2">
            <p>File should contain these columns:</p>
            <button
              onClick={downloadSampleTemplate}
              className="text-blue-400 hover:text-blue-300 text-sm font-medium"
            >
              Download Template
            </button>
          </div>
          <div className="mt-1 text-xs bg-gray-900 p-2 rounded overflow-auto">
            category, subcategory, brand, model, age_years, condition, weight_kg, original_price, scrap_material, location, demand_supply_index, estimated_price
          </div>
          <div className="mt-2 space-y-1">
            <p>Maximum file size: 10MB</p>
            <p>Supported formats: CSV, Excel (.xlsx, .xls)</p>
            <p className="text-xs text-gray-500">Note: All columns are required. Values should be comma-separated in CSV files.</p>
          </div>
        </div>
      </div>
      
      {/* Form Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div>
          <label className="block mb-2 font-medium text-blue-300">Category</label>
          <ComboBox
            value={formData.category}
            onChange={(value) => handleInputChange('category', value)}
            options={['Laptop', 'Mobile', 'Washing Machine', 'Refrigerator', 'TV', 'Tablet']}
            placeholder="Category"
          />
        </div>
        
        <div>
          <label className="block mb-2 font-medium text-blue-300">Subcategory</label>
          <ComboBox
            value={formData.subcategory}
            onChange={(value) => handleInputChange('subcategory', value)}
            options={['Screen', 'Battery', 'Motherboard', 'Circuit Board', 'Casing', 'Power Supply']}
            placeholder="Subcategory"
          />
        </div>
        
        <div>
          <label className="block mb-2 font-medium text-blue-300">Brand</label>
          <ComboBox
            value={formData.brand}
            onChange={(value) => handleInputChange('brand', value)}
            options={['Samsung', 'Apple', 'LG', 'Sony', 'Dell', 'HP', 'Lenovo', 'Whirlpool']}
            placeholder="Brand"
          />
        </div>
        
        <div>
          <label className="block mb-2 font-medium text-blue-300">Model</label>
          <input 
            type="text" 
            name="model"
            value={formData.model}
            onChange={(e) => handleInputChange('model', e.target.value)}
            className="w-full p-2 bg-gray-800 border border-gray-700 rounded text-gray-200 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            placeholder="e.g., Galaxy S10, Inspiron 15"
          />
        </div>
        
        <div>
          <label className="block mb-2 font-medium text-blue-300">Age (years)</label>
          <input 
            type="number" 
            name="age_years"
            value={formData.age_years}
            onChange={(e) => handleInputChange('age_years', parseFloat(e.target.value))}
            className="w-full p-2 bg-gray-800 border border-gray-700 rounded text-gray-200 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            min="0.5"
            max="10"
            step="0.5"
          />
        </div>
        
        <div>
          <label className="block mb-2 font-medium text-blue-300">Condition</label>
          <ComboBox
            value={formData.condition}
            onChange={(value) => handleInputChange('condition', value)}
            options={['Working', 'Faulty', 'Dead', 'Damaged']}
            placeholder="Condition"
          />
        </div>
        
        <div>
          <label className="block mb-2 font-medium text-blue-300">Weight (kg)</label>
          <input 
            type="number" 
            name="weight_kg"
            value={formData.weight_kg}
            onChange={(e) => handleInputChange('weight_kg', parseFloat(e.target.value))}
            className="w-full p-2 bg-gray-800 border border-gray-700 rounded text-gray-200 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            step="0.1"
            min="0.1"
          />
        </div>
        
        <div>
          <label className="block mb-2 font-medium text-blue-300">Original Price (₹)</label>
          <input 
            type="number" 
            name="original_price"
            value={formData.original_price}
            onChange={(e) => handleInputChange('original_price', parseFloat(e.target.value))}
            className="w-full p-2 bg-gray-800 border border-gray-700 rounded text-gray-200 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            step="1000"
            min="1000"
          />
        </div>
        
        <div>
          <label className="block mb-2 font-medium text-blue-300">Scrap Material</label>
          <ComboBox
            value={formData.scrap_material}
            onChange={(value) => handleInputChange('scrap_material', value)}
            options={['Plastic', 'Metal', 'Lithium', 'Copper', 'Gold', 'Silver', 'Aluminum']}
            placeholder="Scrap Material"
          />
        </div>
        
        <div>
          <label className="block mb-2 font-medium text-blue-300">Location</label>
          <ComboBox
            value={formData.location}
            onChange={(value) => handleInputChange('location', value)}
            options={['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Hyderabad', 'Kolkata', 'Pune', 'Ahmedabad']}
            placeholder="Location"
          />
        </div>
        
        <div>
          <label className="block mb-2 font-medium text-blue-300">Demand-Supply Index (0-1)</label>
          <input 
            type="range" 
            name="demand_supply_index"
            value={formData.demand_supply_index}
            onChange={(e) => handleInputChange('demand_supply_index', parseFloat(e.target.value))}
            className="w-full accent-blue-500"
            min="0"
            max="1"
            step="0.1"
          />
          <div className="flex justify-between text-xs text-gray-400">
            <span>Low Demand (0)</span>
            <span>{formData.demand_supply_index}</span>
            <span>High Demand (1)</span>
          </div>
        </div>
      </div>
      
      <div className="text-center">
        <button 
          onClick={handlePredict}
          className="bg-blue-700 text-white px-6 py-3 rounded-lg shadow-md hover:bg-blue-600 disabled:bg-gray-700 disabled:text-gray-500 transition-colors duration-300"
          disabled={!model || !modelTrained || isTraining}
        >
          Calculate Estimated Price
        </button>
      </div>
      
      {prediction && (
        <div className="mt-8 p-6 bg-gray-800 rounded-lg shadow-inner text-center border border-blue-800">
          <h2 className="text-xl font-semibold text-blue-300">Estimated Scrap Value:</h2>
          <p className="text-4xl font-bold text-green-400 my-3">₹ {prediction.toLocaleString('en-IN')}</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
            <div className="bg-gray-900 p-3 rounded shadow border border-gray-800">
              <p className="text-sm text-gray-400">Original Price</p>
              <p className="font-medium text-blue-300">₹ {formData.original_price.toLocaleString('en-IN')}</p>
            </div>
            <div className="bg-gray-900 p-3 rounded shadow border border-gray-800">
              <p className="text-sm text-gray-400">Depreciation</p>
              <p className="font-medium text-blue-300">{Math.round((1 - prediction / formData.original_price) * 100)}%</p>
            </div>
            <div className="bg-gray-900 p-3 rounded shadow border border-gray-800">
              <p className="text-sm text-gray-400">Value Retention</p>
              <p className="font-medium text-blue-300">{Math.round((prediction / formData.original_price) * 100)}%</p>
            </div>
          </div>
          
          {/* Price Factor Visualization */}
          <PriceFactorVisualization prediction={prediction} formData={formData} />
        </div>
      )}
    </div>
  );
};

export default EWastePricePredictorIndia;