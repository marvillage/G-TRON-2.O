import { useEffect } from "react";

const GtronPage = () => {
  useEffect(() => {
    window.location.replace("/gtron.html"); // Replaces current history entry
  }, []);

  return <div>Redirecting...</div>;
};

export default GtronPage;
