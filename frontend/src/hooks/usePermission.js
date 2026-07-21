import { useAuth } from "../context/AuthContext";

export function usePermission() {
  const { user, permissions } = useAuth();

  const hasRole = (allowedRoles) => {
    if (!user) return false;
    if (typeof allowedRoles === "string") {
      return user.role.toLowerCase() === allowedRoles.toLowerCase();
    }
    if (Array.isArray(allowedRoles)) {
      return allowedRoles.map(r => r.toLowerCase()).includes(user.role.toLowerCase());
    }
    return false;
  };

  const hasPermission = (requiredPermission) => {
    if (!permissions) return false;
    return permissions.map(p => p.toLowerCase()).includes(requiredPermission.toLowerCase());
  };

  return { 
    hasRole, 
    hasPermission, 
    role: user?.role, 
    permissions 
  };
}
