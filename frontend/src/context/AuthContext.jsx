import { createContext, useContext, useState, useEffect, useMemo } from "react";
import { authService } from "../services/authService";
import { permissionService } from "../services/permissionService";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [permissions, setPermissions] = useState([]);
  const [loading, setLoading] = useState(true);

  const login = async (username, password) => {
    try {
      await authService.login(username, password);
      const profile = await authService.getCurrentUser();
      setUser(profile);
      
      const rbac = await permissionService.getMyPermissions();
      setPermissions(rbac.permissions || []);
      
      return profile;
    } catch (err) {
      setUser(null);
      setPermissions([]);
      throw err;
    }
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
    setPermissions([]);
  };

  useEffect(() => {
    const initAuth = async () => {
      if (authService.hasSession()) {
        try {
          const profile = await authService.getCurrentUser();
          setUser(profile);
          
          const rbac = await permissionService.getMyPermissions();
          setPermissions(rbac.permissions || []);
        } catch (err) {
          console.error("Session restoration failed:", err);
          setUser(null);
          setPermissions([]);
        }
      }
      setLoading(false);
    };

    initAuth();

    const handleLogoutEvent = () => {
      setUser(null);
      setPermissions([]);
    };

    window.addEventListener("auth_logout", handleLogoutEvent);
    return () => {
      window.removeEventListener("auth_logout", handleLogoutEvent);
    };
  }, []);

  const value = useMemo(() => ({
    user,
    permissions,
    loading,
    login,
    logout,
  }), [user, permissions, loading]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
