import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Polyline } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';
import { format } from 'date-fns';

// Fix for default marker icons in React-Leaflet
const icon = L.icon({
    iconUrl: markerIcon,
    iconRetinaUrl: markerIcon2x,
    shadowUrl: markerShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

const decodePolyline = (encoded) => {
    const points = [];
    let index = 0, lat = 0, lng = 0;

    while (index < encoded.length) {
        let shift = 0, result = 0;
        do {
            let b = encoded.charCodeAt(index++) - 63;
            result |= (b & 0x1f) << shift;
            shift += 5;
        } while (result >= 0x20);
        const dlat = ((result & 1) ? ~(result >> 1) : (result >> 1));
        lat += dlat;

        shift = 0;
        result = 0;
        do {
            let b = encoded.charCodeAt(index++) - 63;
            result |= (b & 0x1f) << shift;
            shift += 5;
        } while (result >= 0x20);
        const dlng = ((result & 1) ? ~(result >> 1) : (result >> 1));
        lng += dlng;

        points.push([lat * 1e-5, lng * 1e-5]);
    }

    return points;
};

const RouteOptimization = () => {
    const [collectionPoints, setCollectionPoints] = useState([]);
    const [trucks, setTrucks] = useState([]);
    const [routePlans, setRoutePlans] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedDate, setSelectedDate] = useState(new Date());
    const [selectedTrucks, setSelectedTrucks] = useState([]);
    const [showMap, setShowMap] = useState(true);

    useEffect(() => {
        fetchInitialData();
    }, []);

    const fetchInitialData = async () => {
        try {
            setLoading(true);
            const response = await fetch('http://localhost:5000/api/initial-data');
            if (!response.ok) {
                throw new Error('Failed to fetch data');
            }
            const data = await response.json();
            setCollectionPoints(data.collection_points);
            setTrucks(data.trucks);
            // Select all trucks by default
            setSelectedTrucks(data.trucks);
        } catch (err) {
            console.error('Error fetching data:', err);
            setError('Failed to load initial data. Please make sure the backend server is running.');
        } finally {
            setLoading(false);
        }
    };

    const handleOptimizeRoutes = async () => {
        if (selectedTrucks.length === 0) {
            setError('Please select at least one truck');
            return;
        }

        setLoading(true);
        setError(null);
        try {
            const response = await fetch('http://localhost:5000/api/optimize-routes', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    collection_points: collectionPoints,
                    trucks: selectedTrucks,
                    date: selectedDate.toISOString(),
                }),
            });
            const data = await response.json();
            if (data.status === 'success') {
                setRoutePlans(data.route_plans);
            } else {
                setError(data.message || 'Failed to optimize routes');
            }
        } catch (err) {
            console.error('Error optimizing routes:', err);
            setError('Failed to optimize routes. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleTruckSelection = (truck) => {
        setSelectedTrucks(prev => {
            if (prev.find(t => t.id === truck.id)) {
                return prev.filter(t => t.id !== truck.id);
            }
            return [...prev, truck];
        });
    };

    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold mb-6">ML-Based Route Optimization</h1>
            
            <div className="mb-6">
                <p className="text-gray-600 mb-4">
                    This page uses ML models to predict waste volumes at each collection point based on 
                    historical patterns, day of week, and area type. It then calculates optimized routes 
                    using the Google Maps API.
                </p>
            </div>

            {/* Date Selection */}
            <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Date for Route Planning
                </label>
                <input
                    type="date"
                    value={format(selectedDate, 'yyyy-MM-dd')}
                    onChange={(e) => setSelectedDate(new Date(e.target.value))}
                    className="border rounded px-3 py-2"
                />
                <p className="text-sm text-gray-500 mt-1">
                    Planning for: {format(selectedDate, 'EEEE, MMMM d, yyyy')}
                </p>
            </div>

            {/* Truck Selection */}
            <div className="mb-6">
                <h2 className="text-xl font-semibold mb-4">Available Trucks</h2>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    {trucks.map((truck) => (
                        <div
                            key={truck.id}
                            className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                                selectedTrucks.find(t => t.id === truck.id)
                                    ? 'border-blue-500 bg-blue-50'
                                    : 'border-gray-200'
                            }`}
                            onClick={() => handleTruckSelection(truck)}
                        >
                            <h3 className="font-medium">{truck.id}</h3>
                            <p className="text-sm text-gray-600">Capacity: {truck.capacity} tons</p>
                            <p className="text-sm text-gray-600">Status: {truck.status}</p>
                        </div>
                    ))}
                </div>
            </div>

            {/* Controls */}
            <div className="mb-6">
                <button
                    onClick={handleOptimizeRoutes}
                    disabled={loading || selectedTrucks.length === 0}
                    className="bg-blue-500 text-white px-6 py-2 rounded-lg disabled:bg-gray-400 hover:bg-blue-600 transition-colors"
                >
                    {loading ? 'Optimizing...' : 'Generate Optimized Routes'}
                </button>
            </div>

            {loading ? (
                <div className="flex justify-center items-center h-64">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
                </div>
            ) : error ? (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                    {error}
                </div>
            ) : routePlans.length > 0 ? (
                <div>
                    <h2 className="text-2xl font-bold mb-6">Optimized Routes</h2>
                    
                    {routePlans.map((plan, index) => (
                        <div key={index} className="border rounded-lg p-6 mb-6">
                            <div className="flex justify-between items-start mb-4">
                                <h3 className="text-xl font-semibold">
                                    Truck {plan.truck_id} (Capacity: {plan.truck_capacity} tons)
                                </h3>
                                {plan.requires_multiple_trips && (
                                    <span className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm">
                                        ⚠️ Requires {plan.min_trips_required} trips
                                    </span>
                                )}
                            </div>

                            {/* Route Metrics */}
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                                <div className="bg-gray-50 p-4 rounded-lg">
                                    <p className="text-sm text-gray-600">Total Distance</p>
                                    <p className="text-xl font-semibold">{plan.total_distance_km.toFixed(1)} km</p>
                                </div>
                                <div className="bg-gray-50 p-4 rounded-lg">
                                    <p className="text-sm text-gray-600">Base Duration</p>
                                    <p className="text-xl font-semibold">{plan.estimated_duration_min.toFixed(0)} min</p>
                                </div>
                                <div className="bg-gray-50 p-4 rounded-lg">
                                    <p className="text-sm text-gray-600">Traffic Duration</p>
                                    <p className="text-xl font-semibold">{plan.total_duration_in_traffic.toFixed(0)} min</p>
                                </div>
                            </div>

                            {/* Traffic Impact */}
                            <div className="mb-6">
                                {plan.traffic_multiplier > 1 ? (
                                    <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
                                        <p className="text-yellow-800">
                                            ⚠️ Traffic adds {(plan.traffic_multiplier - 1) * 100}% to the estimated duration
                                        </p>
                                    </div>
                                ) : plan.traffic_multiplier < 1 ? (
                                    <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
                                        <p className="text-green-800">
                                            ✅ Current traffic conditions are better than average
                                        </p>
                                    </div>
                                ) : (
                                    <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
                                        <p className="text-blue-800">
                                            ℹ️ Current traffic conditions are normal
                                        </p>
                                    </div>
                                )}
                            </div>

                            {/* Route Map */}
                            <div className="mb-6">
                                <div className="h-96">
                                    <MapContainer
                                        center={[21.1458, 79.0882]}
                                        zoom={12}
                                        style={{ height: '100%', width: '100%' }}
                                        scrollWheelZoom={false}
                                    >
                                        <TileLayer
                                            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                                        />
                                        
                                        {/* Add markers and route line */}
                                        {plan.collection_points.map((point, idx) => (
                                            <Marker
                                                key={idx}
                                                position={[point.latitude, point.longitude]}
                                                icon={icon}
                                            />
                                        ))}
                                        
                                        {plan.polyline && (
                                            <Polyline
                                                positions={decodePolyline(plan.polyline)}
                                                color="blue"
                                                weight={3}
                                            />
                                        )}
                                    </MapContainer>
                                </div>
                            </div>

                            {/* Collection Points Table */}
                            <div className="overflow-x-auto">
                                <table className="min-w-full divide-y divide-gray-200">
                                    <thead className="bg-gray-50">
                                        <tr>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stop #</th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Location</th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Predicted Waste (tons)</th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Area Type</th>
                                        </tr>
                                    </thead>
                                    <tbody className="bg-white divide-y divide-gray-200">
                                        {plan.collection_points.map((point, idx) => (
                                            <tr key={idx}>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{idx + 1}</td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{point.location_name}</td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{point.predicted_waste_tons.toFixed(1)}</td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{point.area_type}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    ))}
                </div>
            ) : null}
        </div>
    );
};

export default RouteOptimization;
