import { Navigate } from "react-router-dom";
import PropTypes from "prop-types";

PrivateRoute.propTypes = {
  children: PropTypes.node.isRequired,
};

export default function PrivateRoute({ children }) {
  const token = localStorage.getItem("access");
  return token ? children : <Navigate to="/login" replace />;
}
