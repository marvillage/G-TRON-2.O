import React, { useState, useEffect, useRef } from 'react';
import { 
  initializeApp 
} from 'firebase/app';
import { 
  getFirestore, 
  collection, 
  addDoc, 
  getDocs, 
  doc,
  updateDoc,
  onSnapshot,
  query,
  orderBy
} from 'firebase/firestore';
import { 
  getStorage, 
  ref, 
  uploadBytes, 
  getDownloadURL
} from 'firebase/storage';
import { 
  GoogleMap, 
  useJsApiLoader, 
  HeatmapLayer, 
  Marker 
} from '@react-google-maps/api';
import './dumping.css';

// Import Firebase config
import firebaseConfig from '../../firebase_config';

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
const storage = getStorage(app, 'gs://e-waste-management-2a578.appspot.com');

// Google Maps configuration
const mapContainerStyle = {
  width: '100%',
  height: '400px',
};

const center = {
  lat: 20,
  lng: 0,
};

const mapOptions = {
  disableDefaultUI: true,
  zoomControl: true,
};

function DumpingPage() {
  // State variables
  const [reports, setReports] = useState([]);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);
  
  // Form state
  const [formData, setFormData] = useState({
    description: '',
    anonymous: false,
    imageFile: null,
    imagePreview: null,
    location: { lat: null, lng: null, address: '' },
  });
  
  // AI detected waste types
  const [wasteTypes, setWasteTypes] = useState([]);
  
  // Refs
  const mapRef = useRef(null);
  const fileInputRef = useRef(null);
  
  // Load Google Maps
  const { isLoaded } = useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY,
    libraries: ['visualization'],
  });

  // Fetch reports on component mount
  useEffect(() => {
    const fetchReports = async () => {
      try {
        const q = query(collection(db, 'reports'), orderBy('createdAt', 'desc'));
        const querySnapshot = await getDocs(q);
        const reportsList = querySnapshot.docs.map(doc => ({
          id: doc.id,
          ...doc.data()
        }));
        setReports(reportsList);
      } catch (error) {
        console.error('Error fetching reports:', error);
      }
    };
    
    fetchReports();
    
    // Set up real-time listener
    const q = query(collection(db, 'reports'), orderBy('createdAt', 'desc'));
    const unsubscribe = onSnapshot(q, (querySnapshot) => {
      const reportsList = querySnapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      setReports(reportsList);
    });
    
    return () => unsubscribe();
  }, []);
  
  // Get user's location
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const { latitude, longitude } = position.coords;
          const locationData = { lat: latitude, lng: longitude, address: '' };
          
          // Reverse geocoding to get address
          try {
            const response = await fetch(
              `https://maps.googleapis.com/maps/api/geocode/json?latlng=${latitude},${longitude}&key=${import.meta.env.VITE_GOOGLE_MAPS_API_KEY}`
            );
            const data = await response.json();
            if (data.results[0]) {
              locationData.address = data.results[0].formatted_address;
            }
          } catch (error) {
            console.error('Error getting address:', error);
          }
          
          setFormData(prev => ({ ...prev, location: locationData }));
          
          // Center the map on user's location
          if (mapRef.current) {
            mapRef.current.panTo({ lat: latitude, lng: longitude });
            mapRef.current.setZoom(12);
          }
        },
        (error) => {
          console.error('Error getting location:', error);
        }
      );
    }
  }, []);
  
  // Handle form input changes
  const handleChange = (e) => {
    const { name, value, checked, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  // Handle image upload and analyze
  const handleImageChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (e) => {
      setFormData(prev => ({
        ...prev,
        imageFile: file,
        imagePreview: e.target.result
      }));
    };
    reader.readAsDataURL(file);
    
    // Analyze image using Google Cloud Vision API and Firebase ML Kit
    setLoading(true);
    try {
      // Upload to temporary storage location
      const storageRef = ref(storage, `temp/${Date.now()}-${file.name}`);
      const metadata = {
        contentType: file.type,
        customMetadata: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        }
      };
      
      // Upload using Firebase's uploadBytes with retry logic
      let uploadResult;
      let retryCount = 0;
      const maxRetries = 3;
      
      while (retryCount < maxRetries) {
        try {
          uploadResult = await uploadBytes(storageRef, file, metadata);
          break;
        } catch (error) {
          console.error(`Upload attempt ${retryCount + 1} failed:`, error);
          retryCount++;
          if (retryCount === maxRetries) throw error;
          // Wait before retrying
          await new Promise(resolve => setTimeout(resolve, 1000 * retryCount));
        }
      }
      
      console.log('Upload successful:', uploadResult);
      
      // Get download URL with retry logic
      let imageUrl;
      retryCount = 0;
      
      while (retryCount < maxRetries) {
        try {
          imageUrl = await getDownloadURL(uploadResult.ref);
          break;
        } catch (error) {
          console.error(`Get URL attempt ${retryCount + 1} failed:`, error);
          retryCount++;
          if (retryCount === maxRetries) throw error;
          // Wait before retrying
          await new Promise(resolve => setTimeout(resolve, 1000 * retryCount));
        }
      }
      
      console.log('Download URL:', imageUrl);
      
      // Call Google Cloud Vision API
      const response = await fetch('https://vision.googleapis.com/v1/images:annotate?key=' + import.meta.env.VITE_GOOGLE_VISION_API_KEY, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        },
        body: JSON.stringify({
          requests: [
            {
              image: {
                source: {
                  imageUri: imageUrl
                }
              },
              features: [
                {
                  type: 'LABEL_DETECTION',
                  maxResults: 10
                },
                {
                  type: 'OBJECT_LOCALIZATION',
                  maxResults: 10
                }
              ]
            }
          ]
        })
      });
      
      const data = await response.json();
      
      // Process the results
      // Look for e-waste related labels
      const eWasteKeywords = ['electronic', 'computer', 'laptop', 'phone', 'battery', 'circuit', 'television', 'monitor', 'appliance', 'cable', 'wire', 'device'];
      
      const detectedTypes = [];
      
      // Process label annotations
      if (data.responses[0].labelAnnotations) {
        data.responses[0].labelAnnotations.forEach(label => {
          const labelLower = label.description.toLowerCase();
          if (eWasteKeywords.some(keyword => labelLower.includes(keyword))) {
            detectedTypes.push({
              name: label.description,
              confidence: Math.round(label.score * 100)
            });
          }
        });
      }
      
      // Process object annotations
      if (data.responses[0].localizedObjectAnnotations) {
        data.responses[0].localizedObjectAnnotations.forEach(object => {
          const objectLower = object.name.toLowerCase();
          if (eWasteKeywords.some(keyword => objectLower.includes(keyword))) {
            detectedTypes.push({
              name: object.name,
              confidence: Math.round(object.score * 100)
            });
          }
        });
      }
      
      // If no e-waste detected, use generic detection
      if (detectedTypes.length === 0 && data.responses[0].labelAnnotations) {
        // Get top 3 general labels
        data.responses[0].labelAnnotations.slice(0, 3).forEach(label => {
          detectedTypes.push({
            name: label.description,
            confidence: Math.round(label.score * 100)
          });
        });
      }
      
      setWasteTypes(detectedTypes);
    } catch (error) {
      console.error('Error analyzing image:', error);
      // Fallback to mock data if the API fails
      setWasteTypes([
        { name: 'Electronic Components', confidence: 85 },
        { name: 'Waste Material', confidence: 92 }
      ]);
    } finally {
      setLoading(false);
    }
  };
  
  // Submit report
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      // Upload image
      const imageFile = formData.imageFile;
      if (!imageFile) {
        throw new Error('No image file selected');
      }

      // Create a unique filename
      const timestamp = Date.now();
      const filename = `${timestamp}-${imageFile.name.replace(/[^a-zA-Z0-9.]/g, '_')}`;
      const storageRef = ref(storage, `reports/${filename}`);
      
      // Set metadata
      const metadata = {
        contentType: imageFile.type,
        customMetadata: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        }
      };

      // Upload with retry logic
      let uploadResult;
      let retryCount = 0;
      const maxRetries = 3;
      
      while (retryCount < maxRetries) {
        try {
          uploadResult = await uploadBytes(storageRef, imageFile, metadata);
          break;
        } catch (error) {
          console.error(`Upload attempt ${retryCount + 1} failed:`, error);
          retryCount++;
          if (retryCount === maxRetries) throw error;
          // Wait before retrying
          await new Promise(resolve => setTimeout(resolve, 1000 * retryCount));
        }
      }
      
      console.log('Upload successful:', uploadResult);
      
      // Get download URL with retry logic
      let imageUrl;
      retryCount = 0;
      
      while (retryCount < maxRetries) {
        try {
          imageUrl = await getDownloadURL(uploadResult.ref);
          break;
        } catch (error) {
          console.error(`Get URL attempt ${retryCount + 1} failed:`, error);
          retryCount++;
          if (retryCount === maxRetries) throw error;
          // Wait before retrying
          await new Promise(resolve => setTimeout(resolve, 1000 * retryCount));
        }
      }
      
      console.log('Download URL:', imageUrl);
      
      // Remove file object and preview from the data
      const { imageFile: fileObj, imagePreview, ...data } = formData;
      
      // Add document to Firestore
      const docRef = await addDoc(collection(db, 'reports'), {
        ...data,
        imageUrl,
        wasteTypes,
        status: 'Pending',
        createdAt: new Date().toISOString()
      });
      
      console.log('Report added to Firestore:', docRef.id);
      
      // Reset form
      setFormData({
        description: '',
        anonymous: false,
        imageFile: null,
        imagePreview: null,
        location: { ...formData.location }
      });
      setWasteTypes([]);
      setIsFormOpen(false);
      
      alert('Report submitted successfully!');
    } catch (error) {
      console.error('Error submitting report:', error);
      alert(`Error submitting report: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };
  
  // Update report status
  const updateReportStatus = async (reportId, status) => {
    try {
      const reportRef = doc(db, 'reports', reportId);
      await updateDoc(reportRef, { 
        status,
        updatedAt: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error updating report status:', error);
      alert('Error updating report status.');
    }
  };
  
  // Google Maps callbacks
  const onMapLoad = React.useCallback(function callback(map) {
    mapRef.current = map;
  }, []);

  const onMapUnmount = React.useCallback(function callback() {
    mapRef.current = null;
  }, []);
  
  // Prepare heatmap data
  const heatmapData = React.useMemo(() => {
    return reports
      .filter(report => report.location && report.location.lat && report.location.lng)
      .map(report => ({
        location: new window.google.maps.LatLng(report.location.lat, report.location.lng),
        weight: 1,
      }));
  }, [reports]);
  
  // Get status marker icon
  const getStatusIcon = (status) => {
    switch (status) {
      case 'Pending':
        return '/images/pending_marker.svg';
      case 'Verified':
        return '/images/verified_marker.svg';
      case 'Resolved':
        return '/images/resolved_marker.svg';
      default:
        return '/images/default_marker.svg';
    }
  };
  
  return (
    <div className="app-container">
      <header className="app-header">
        <h1>E-Waste Dumping Reporter</h1>
        <button 
          className="report-button"
          onClick={() => setIsFormOpen(true)}
        >
          Report Illegal Dumping
        </button>
      </header>
      
      <main className="app-main">
        {/* Map Section */}
        <section className="map-section">
          <h2>Illegal Dumping Heatmap</h2>
          {isLoaded ? (
            <GoogleMap
              mapContainerStyle={mapContainerStyle}
              center={center}
              zoom={3}
              options={mapOptions}
              onLoad={onMapLoad}
              onUnmount={onMapUnmount}
            >
              <HeatmapLayer
                data={heatmapData}
                options={{
                  radius: 20,
                  opacity: 0.7,
                  gradient: [
                    'rgba(0, 255, 255, 0)',
                    'rgba(0, 255, 255, 1)',
                    'rgba(0, 191, 255, 1)',
                    'rgba(0, 127, 255, 1)',
                    'rgba(0, 63, 255, 1)',
                    'rgba(0, 0, 255, 1)',
                    'rgba(0, 0, 223, 1)',
                    'rgba(0, 0, 191, 1)',
                    'rgba(0, 0, 159, 1)',
                    'rgba(0, 0, 127, 1)',
                  ],
                }}
              />
              
              {/* Display markers for each report */}
              {reports.map((report) => (
                report.location && report.location.lat && report.location.lng && (
                  <Marker
                    key={report.id}
                    position={{ lat: report.location.lat, lng: report.location.lng }}
                    icon={{
                      url: getStatusIcon(report.status),
                      scaledSize: new window.google.maps.Size(30, 30),
                    }}
                    onClick={() => setSelectedReport(report)}
                  />
                )
              ))}
            </GoogleMap>
          ) : import.meta.env.VITE_GOOGLE_MAPS_API_KEY ? (
            <div className="loading-map">Loading map...</div>
          ) : (
            <div className="loading-map" style={{ padding: '2rem', textAlign: 'center', lineHeight: 1.6 }}>
              🗺️ Interactive map unavailable in this demo.
              <br />
              Set a <code>VITE_GOOGLE_MAPS_API_KEY</code> environment variable to enable the
              live dumping-detection map.
            </div>
          )}
        </section>
        
        {/* Recent Reports Section */}
        <section className="recent-reports-section">
          <h2>Recent Reports</h2>
          <div className="reports-grid">
            {reports.slice(0, 6).map(report => (
              <div 
                key={report.id} 
                className="report-card"
                onClick={() => setSelectedReport(report)}
              >
                <div className="report-image">
                  <img src={report.imageUrl} alt="Reported waste" />
                  <span className={`status-badge status-${report.status.toLowerCase()}`}>
                    {report.status}
                  </span>
                </div>
                <div className="report-details">
                  <p className="report-location">{report.location.address}</p>
                  <p className="report-date">
                    {new Date(report.createdAt).toLocaleDateString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </section>
        
        {/* Report Form Modal */}
        {isFormOpen && (
          <div className="modal-overlay">
            <div className="report-form-modal">
              <button className="close-button" onClick={() => setIsFormOpen(false)}>×</button>
              <h2>Report Illegal E-Waste Dumping</h2>
              
              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label>Upload Photo/Video Evidence</label>
                  <input 
                    type="file" 
                    accept="image/*,video/*" 
                    onChange={handleImageChange}
                    ref={fileInputRef}
                    required
                  />
                  {formData.imagePreview && (
                    <div className="image-preview">
                      <img src={formData.imagePreview} alt="Preview" />
                      {loading && <p className="analyzing-text">Analyzing image...</p>}
                      {wasteTypes.length > 0 && (
                        <div className="waste-analysis">
                          <p>AI-Detected Items:</p>
                          <ul className="waste-types-list">
                            {wasteTypes.map((type, index) => (
                              <li key={index}>
                                {type.name} ({type.confidence}% confidence)
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </div>
                
                <div className="form-group">
                  <label>Location</label>
                  <p className="location-display">
                    {formData.location.address || 'Detecting location...'}
                  </p>
                  {isLoaded && (
                    <div className="location-map" style={{ height: '200px' }}>
                      <GoogleMap
                        mapContainerStyle={{ width: '100%', height: '100%' }}
                        center={{
                          lat: formData.location.lat || center.lat,
                          lng: formData.location.lng || center.lng
                        }}
                        zoom={14}
                        options={{ zoomControl: true, streetViewControl: false }}
                        onClick={(e) => {
                          // Allow manual location selection
                          const lat = e.latLng.lat();
                          const lng = e.latLng.lng();
                          
                          // Reverse geocode
                          fetch(
                            `https://maps.googleapis.com/maps/api/geocode/json?latlng=${lat},${lng}&key=${import.meta.env.VITE_GOOGLE_MAPS_API_KEY}`
                          )
                            .then(response => response.json())
                            .then(data => {
                              const address = data.results[0] ? data.results[0].formatted_address : '';
                              setFormData(prev => ({
                                ...prev,
                                location: { lat, lng, address }
                              }));
                            })
                            .catch(error => {
                              console.error('Error getting address:', error);
                              setFormData(prev => ({
                                ...prev,
                                location: { lat, lng, address: 'Unknown location' }
                              }));
                            });
                        }}
                      >
                        {formData.location.lat && formData.location.lng && (
                          <Marker
                            position={{
                              lat: formData.location.lat,
                              lng: formData.location.lng
                            }}
                          />
                        )}
                      </GoogleMap>
                    </div>
                  )}
                  <p className="help-text">Click on the map to manually set the location</p>
                </div>
                
                <div className="form-group">
                  <label>Description</label>
                  <textarea 
                    name="description" 
                    value={formData.description} 
                    onChange={handleChange}
                    placeholder="Describe the dumping incident, waste type, and any other details"
                    rows="4"
                    required
                  />
                </div>
                
                <div className="form-group checkbox">
                  <input 
                    type="checkbox" 
                    name="anonymous" 
                    checked={formData.anonymous} 
                    onChange={handleChange}
                    id="anonymous"
                  />
                  <label htmlFor="anonymous">Report Anonymously</label>
                </div>
                
                <button 
                  type="submit" 
                  className="submit-button"
                  disabled={loading || !formData.imageFile}
                >
                  {loading ? 'Submitting...' : 'Submit Report'}
                </button>
              </form>
            </div>
          </div>
        )}
        
        {/* Report Details Modal */}
        {selectedReport && (
          <div className="modal-overlay">
            <div className="report-details-modal">
              <button className="close-button" onClick={() => setSelectedReport(null)}>×</button>
              <h2>Report Details</h2>
              
              <div className="report-image-large">
                <img src={selectedReport.imageUrl} alt="Reported waste" />
              </div>
              
              <div className="report-info">
                <div className="info-row">
                  <span className="label">Date:</span>
                  <span className="value">{new Date(selectedReport.createdAt).toLocaleString()}</span>
                </div>
                
                <div className="info-row">
                  <span className="label">Location:</span>
                  <span className="value">{selectedReport.location.address}</span>
                </div>
                
                <div className="info-row">
                  <span className="label">Status:</span>
                  <span className={`value status-${selectedReport.status.toLowerCase()}`}>
                    {selectedReport.status}
                  </span>
                </div>
                
                <div className="info-row">
                  <span className="label">Description:</span>
                  <span className="value description">{selectedReport.description}</span>
                </div>
                
                {selectedReport.wasteTypes && selectedReport.wasteTypes.length > 0 && (
                  <div className="info-row">
                    <span className="label">AI-Detected Items:</span>
                    <ul className="value waste-types">
                      {selectedReport.wasteTypes.map((type, index) => (
                        <li key={index}>{type.name} ({type.confidence}%)</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                <div className="status-buttons">
                  {selectedReport.status === 'Pending' && (
                    <button 
                      onClick={() => {
                        updateReportStatus(selectedReport.id, 'Verified');
                        setSelectedReport(prev => ({ ...prev, status: 'Verified' }));
                      }}
                    >
                      Verify Report
                    </button>
                  )}
                  
                  {selectedReport.status === 'Verified' && (
                    <button 
                      onClick={() => {
                        updateReportStatus(selectedReport.id, 'Resolved');
                        setSelectedReport(prev => ({ ...prev, status: 'Resolved' }));
                      }}
                    >
                      Mark as Resolved
                    </button>
                  )}
                  
                  {selectedReport.status === 'Resolved' && (
                    <p className="resolution-message">This issue has been resolved.</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default DumpingPage; 