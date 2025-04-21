import { useEffect } from "react";

const EWasteDetection = () => {
  useEffect(() => {
    window.location.replace("/live.html"); // Replaces current history entry
  }, []);

  return <div>Redirecting...</div>;
};

export default EWasteDetection;
