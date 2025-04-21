import { useEffect } from "react";

const GtronPage = () => {
  useEffect(() => {
    window.location.replace("/carbon.html"); // Replaces current history entry
  }, []);

  return <div>Redirecting...</div>;
};

export default GtronPage;
