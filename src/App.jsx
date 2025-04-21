import { createBrowserRouter, RouterProvider } from "react-router-dom";

import { ThemeProvider } from "@/contexts/theme-context";
import { Navigate } from "react-router-dom";
import Layout from "@/routes/layout";
import DashboardPage from "@/routes/dashboard/page";
import DumpingPage from "@/routes/dumping/page";
import EWastePricePredictorIndia from "@/components/EWastePricePredictorIndia.jsx";
import GtronPage from "./components/GtronPage";
import Carbon from "./components/carbon";
import EWasteDetection from "./components/e-wastedetection";
import StreamlitEmbedPage from "./components/StreamlitEmbedPage";

function App() {
    const router = createBrowserRouter([
        {
            path: "/",
            element: <Layout />,
            children: [
                {
                    index: true,
                    element: <DashboardPage />,
                },
                
                {
                    path: "dumping",
                    element: <DumpingPage />,
                },
                {
                    path: "lifecycle",
                    element: <StreamlitEmbedPage 
                               title="Lifecycle Prediction" 
                               url="http://localhost:8503?embed=true"
                             />,
                },
                {
                    path: "classification",
                    element: <StreamlitEmbedPage 
                               title="AI Waste Classification" 
                               url="http://localhost:8504?embed=true"
                             />,
                },
                {
                    path: "dataset/ewassteanalytics/wa",
                    element: <StreamlitEmbedPage 
                               title="E-Waste Analytics" 
                               url="http://localhost:8513?embed=true"
                             />,
                },
                
                
                {
                    
                        path: "gtron",
                        element: <GtronPage />,
                      
                      
                },
                {
                    path: "toxmat",
                    element: <StreamlitEmbedPage 
                               title="Toxic Material Detection" 
                               url="http://localhost:8505?embed=true"
                             />,
                },
                {
                    path: "route",
                    element: <StreamlitEmbedPage 
                               title="ML-Based Route Optimization" 
                               url="http://localhost:8507?embed=true"
                             />,
                },
                {
                    path: "illegal",
                    element: <StreamlitEmbedPage 
                               title="Illegal Dumping Alerts" 
                               url="http://localhost:8508?embed=true"
                             />, 
                },
                {
                    path: "iotsensor",
                    element: <StreamlitEmbedPage 
                               title="Anomaly Detection" 
                               url="http://localhost:8506?embed=true"
                             />, 
                },
                {
                    path: "esg",
                    element: <StreamlitEmbedPage 
                               title="ESG Tracking" 
                               url="http://localhost:8520?embed=true"
                             />,
                },
                {
                    path: "ma",
                    element: <StreamlitEmbedPage 
                               title="Material Recovery" 
                               url="http://localhost:8519?embed=true"
                             />,
                },
                {
                    path: "epr",
                    element: <StreamlitEmbedPage 
                               title="EPR Tracking" 
                               url="http://localhost:8502?embed=true"
                             />,
                },
                {
                    path: "e-wastedetection",
                    element: <EWasteDetection />,
                },
                {
                    path: "compliance",
                    element: <StreamlitEmbedPage 
                               title="Compliance Reports" 
                               url="http://localhost:8512?embed=true"
                             />,
                },
                {
                    path: "buyrecycle",
                    element: <StreamlitEmbedPage 
                               title="Buy Recycle" 
                               url="http://localhost:8516?embed=true"
                             />,
                },
                {
                    
                    path: "carbon",
                    element: <Carbon />,
                  
                  
            },

                {
                    path: "pricing",
                    element: <EWastePricePredictorIndia />,
                },
                {
                    path: "analytics",
                    element: <h1 className="title">Analytics</h1>,
                },
                {
                    path: "reports",
                    element: <h1 className="title">Reports</h1>,
                },
                {
                    path: "customers",
                    element: <h1 className="title">Customers</h1>,
                },
                {
                    path: "new-customer",
                    element: <h1 className="title">New Customer</h1>,
                },
                {
                    path: "verified-customers",
                    element: <h1 className="title">Verified Customers</h1>,
                },
                {
                    path: "products",
                    element: <h1 className="title">Products</h1>,
                },
                {
                    path: "new-product",
                    element: <h1 className="title">New Product</h1>,
                },
                {
                    path: "inventory",
                    element: <h1 className="title">Inventory</h1>,
                },
                {
                    path: "settings",
                    element: <h1 className="title">Settings</h1>,
                },
            ],
        },
    ]);

    return (
        <ThemeProvider storageKey="theme">
            <RouterProvider router={router} />
        </ThemeProvider>
    );
}

export default App;
