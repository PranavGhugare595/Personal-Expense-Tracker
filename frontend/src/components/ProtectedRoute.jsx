import { Navigate, Outlet } from 'react-router-dom';

const ProtectedRoute = () => {
  const token = localStorage.getItem('token');
  
  if (!token) {
    // If no token, redirect to login
    return <Navigate to="/login" replace />;
  }

  // Assuming the token is valid; actual verification happens on API calls
  // If the token is expired, the API interceptor in api.js will handle the 401
  // and redirect the user back to /login
  
  return <Outlet />;
};

export default ProtectedRoute;
