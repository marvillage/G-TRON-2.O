import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const PriceFactorVisualization = ({ prediction, formData }) => {
  // Calculate hypothetical impact of different factors
  const calculateImpact = () => {
    // These factors are just estimates for visualization purposes
    // In a real app, you would derive these from your model
    
    const impactFactors = [
      {
        name: 'Category',
        impact: formData.category === 'Laptop' ? 0.25 : 
                formData.category === 'Mobile' ? 0.2 : 
                formData.category === 'TV' ? 0.15 : 0.1,
        description: 'Higher value for laptops and mobiles due to recoverable components'
      },
      {
        name: 'Condition',
        impact: formData.condition === 'Working' ? 0.3 : 
                formData.condition === 'Faulty' ? 0.2 : 
                formData.condition === 'Damaged' ? 0.1 : 0.05,
        description: 'Working items retain significantly more value'
      },
      {
        name: 'Age',
        impact: Math.max(0, 0.25 - (formData.age_years * 0.025)),
        description: 'Newer items have higher recycling value'
      },
      {
        name: 'Material',
        impact: formData.scrap_material === 'Gold' ? 0.4 :
                formData.scrap_material === 'Silver' ? 0.25 :
                formData.scrap_material === 'Copper' ? 0.2 : 
                formData.scrap_material === 'Lithium' ? 0.15 : 0.1,
        description: 'Precious metals significantly increase recycling value'
      },
      {
        name: 'Demand',
        impact: formData.demand_supply_index * 0.2,
        description: 'Higher market demand increases price'
      },
      {
        name: 'Weight',
        impact: Math.min(0.25, formData.weight_kg * 0.01),
        description: 'Heavier items often contain more recoverable material'
      }
    ];
    
    // Normalize impacts to make them relative to prediction
    const totalImpact = impactFactors.reduce((sum, factor) => sum + factor.impact, 0);
    const scaleFactor = prediction / totalImpact;
    
    return impactFactors.map(factor => ({
      ...factor,
      value: Math.round(factor.impact * scaleFactor)
    }));
  };

  const data = calculateImpact();

  return (
    <div className="mt-6 p-4 bg-white rounded-lg shadow">
      <h3 className="text-lg font-medium mb-4">Value Contributors</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart
          data={data}
          margin={{
            top: 20, right: 30, left: 20, bottom: 50,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" angle={-45} textAnchor="end" height={70} />
          <YAxis label={{ value: 'Impact on Value (₹)', angle: -90, position: 'insideLeft' }} />
          <Tooltip 
            formatter={(value) => [`₹${value}`, 'Impact']}
            labelFormatter={(name) => `Factor: ${name}`}
            content={({ active, payload, label }) => {
              if (active && payload && payload.length) {
                const item = data.find(d => d.name === label);
                return (
                  <div className="bg-white p-3 border shadow-sm">
                    <p className="font-bold">{label}</p>
                    <p className="text-green-600">₹{payload[0].value}</p>
                    <p className="text-sm mt-1">{item.description}</p>
                  </div>
                );
              }
              return null;
            }}
          />
          <Bar dataKey="value" fill="#4C9AFF" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default PriceFactorVisualization;