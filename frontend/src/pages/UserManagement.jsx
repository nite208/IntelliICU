import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Users,
  Search,
  Plus,
  Edit2,
  Trash2,
  Lock,
  UserCheck,
  UserX,
  X,
  Shield,
  Briefcase,
  Mail,
  ChevronLeft,
  ChevronRight,
  ShieldAlert,
} from "lucide-react";
import { userService } from "../services/userService";
import { permissionService } from "../services/permissionService";

export default function UserManagement() {
  const [users, setUsers] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [size] = useState(8);
  
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("all");
  const [deptFilter, setDeptFilter] = useState("all");

  const [roles, setRoles] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Dialog states
  const [addOpen, setAddOpen] = useState(false);
  const [editOpen, setEditOpen] = useState(false);
  const [resetOpen, setResetOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);

  // Form states
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("");
  const [department, setDepartment] = useState("");
  const [isActive, setIsActive] = useState(true);
  const [newPassword, setNewPassword] = useState("");

  const loadData = async () => {
    try {
      setLoading(true);
      setError("");
      const data = await userService.getUsers(search, roleFilter, deptFilter, page, size);
      setUsers(data.users || []);
      setTotal(data.total || 0);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch user accounts directory.");
    } finally {
      setLoading(false);
    }
  };

  const loadMetaData = async () => {
    try {
      const rolesData = await permissionService.getAllRoles();
      setRoles(rolesData || []);
      const deptsData = await userService.getDepartments();
      setDepartments(deptsData || []);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadMetaData();
  }, []);

  useEffect(() => {
    setPage(1);
  }, [search, roleFilter, deptFilter]);

  useEffect(() => {
    loadData();
  }, [search, roleFilter, deptFilter, page]);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!username.trim() || !email.trim() || !password.trim() || !role) {
      setError("Please fill out all required fields.");
      return;
    }
    try {
      setLoading(true);
      setError("");
      await userService.createUser({
        username,
        email,
        password,
        role,
        department: department || null,
      });
      setAddOpen(false);
      resetForms();
      loadData();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to create user account.");
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    if (!selectedUser || !email.trim() || !role) {
      setError("Please fill out all required fields.");
      return;
    }
    try {
      setLoading(true);
      setError("");
      await userService.updateUser(selectedUser.id, {
        email,
        role,
        department: department || null,
        is_active: isActive,
      });
      setEditOpen(false);
      resetForms();
      loadData();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update user details.");
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    if (!selectedUser || !newPassword.trim()) {
      setError("Please enter a new password.");
      return;
    }
    try {
      setLoading(true);
      setError("");
      await userService.resetUserPassword(selectedUser.id, newPassword);
      setResetOpen(false);
      resetForms();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to reset password.");
    } finally {
      setLoading(false);
    }
  };

  const handleDeactivate = async (user) => {
    if (!window.confirm(`Are you sure you want to deactivate account: ${user.username}?`)) {
      return;
    }
    try {
      setLoading(true);
      await userService.deactivateUser(user.id);
      loadData();
    } catch (err) {
      alert("Failed to deactivate account.");
    } finally {
      setLoading(false);
    }
  };

  const openEdit = (user) => {
    setSelectedUser(user);
    setEmail(user.email);
    setRole(user.role);
    setDepartment(user.department || "");
    setIsActive(user.is_active);
    setEditOpen(true);
  };

  const openReset = (user) => {
    setSelectedUser(user);
    setNewPassword("");
    setResetOpen(true);
  };

  const resetForms = () => {
    setUsername("");
    setEmail("");
    setPassword("");
    setRole("");
    setDepartment("");
    setIsActive(true);
    setNewPassword("");
    setSelectedUser(null);
    setError("");
  };

  const totalPages = Math.ceil(total / size) || 1;

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-100 pb-5">
        <div>
          <h1 className="text-3xl font-black text-slate-800">User Management</h1>
          <p className="mt-1 text-xs text-slate-500">Manage clinical suite system users, roles, and department profiles</p>
        </div>
        <button
          onClick={() => { resetForms(); setAddOpen(true); }}
          className="btn-clinical-primary"
        >
          <Plus size={14} />
          Create New User
        </button>
      </div>

      {/* Info Stats grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="clinical-card p-5 flex items-center gap-4">
          <div className="h-10 w-10 rounded-xl bg-cyan-50 text-cyan-600 flex items-center justify-center shadow-sm border border-cyan-100/20">
            <Users size={18} />
          </div>
          <div>
            <span className="clinical-label text-[10px] text-slate-400">Total Records</span>
            <span className="text-xl font-black text-slate-800 mt-0.5 block leading-none">{total}</span>
          </div>
        </div>
        <div className="clinical-card p-5 flex items-center gap-4">
          <div className="h-10 w-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center shadow-sm border border-emerald-100/20">
            <UserCheck size={18} />
          </div>
          <div>
            <span className="clinical-label text-[10px] text-slate-400">Active Users</span>
            <span className="text-xl font-black text-slate-800 mt-0.5 block leading-none">
              {users.filter(u => u.is_active).length}
            </span>
          </div>
        </div>
        <div className="clinical-card p-5 flex items-center gap-4">
          <div className="h-10 w-10 rounded-xl bg-red-50 text-red-650 flex items-center justify-center shadow-sm border border-red-100/20">
            <UserX size={18} />
          </div>
          <div>
            <span className="clinical-label text-[10px] text-slate-400">Deactivated</span>
            <span className="text-xl font-black text-slate-800 mt-0.5 block leading-none">
              {users.filter(u => !u.is_active).length}
            </span>
          </div>
        </div>
      </div>

      {/* Filter toolbar */}
      <div className="flex flex-col sm:flex-row items-center gap-4 bg-slate-50/50 p-4.5 rounded-2xl border border-slate-100">
        <div className="relative flex-1 w-full">
          <Search size={14} className="absolute left-3.5 top-3.5 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search users by name or email..."
            className="input-clinical pl-10"
          />
        </div>
        <div className="flex items-center gap-3 w-full sm:w-auto">
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="input-clinical w-full sm:w-40 font-bold"
          >
            <option value="all">All Roles</option>
            {roles.map(r => <option key={r.id} value={r.name}>{r.name}</option>)}
          </select>
          <select
            value={deptFilter}
            onChange={(e) => setDeptFilter(e.target.value)}
            className="input-clinical w-full sm:w-48 font-bold"
          >
            <option value="all">All Departments</option>
            {departments.map(d => <option key={d.id} value={d.name}>{d.name}</option>)}
          </select>
        </div>
      </div>

      {/* Grid List View */}
      <div className="clinical-card shadow-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="table-clinical">
            <thead>
              <tr>
                <th className="th-clinical">User Profile</th>
                <th className="th-clinical">Security Role</th>
                <th className="th-clinical">Department</th>
                <th className="th-clinical">Account Status</th>
                <th className="th-clinical text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="text-xs font-semibold text-slate-600">
              {users.length > 0 ? (
                users.map((user) => (
                  <tr key={user.id} className="hover:bg-slate-50/40 transition">
                    <td className="td-clinical flex items-center gap-3">
                      <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-slate-100 to-slate-200/50 flex items-center justify-center font-bold text-slate-600 uppercase shadow-sm border border-slate-200/30 text-xs">
                        {user.username.slice(0, 2)}
                      </div>
                      <div>
                        <h4 className="font-bold text-slate-800 text-sm leading-tight">{user.username}</h4>
                        <span className="text-[10px] text-slate-400 mt-0.5 block flex items-center gap-1">
                          <Mail size={10} />
                          {user.email}
                        </span>
                      </div>
                    </td>
                    <td className="td-clinical">
                      <span className="badge-clinical-info">
                        <Shield size={10} />
                        {user.role}
                      </span>
                    </td>
                    <td className="td-clinical">
                      {user.department ? (
                        <span className="badge-clinical-success">
                          <Briefcase size={10} />
                          {user.department}
                        </span>
                      ) : (
                        <span className="text-slate-400">-</span>
                      )}
                    </td>
                    <td className="td-clinical">
                      {user.is_active ? (
                        <span className="badge-clinical-success">Active</span>
                      ) : (
                        <span className="badge-clinical-danger">Inactive</span>
                      )}
                    </td>
                    <td className="td-clinical text-right">
                      <div className="flex justify-end gap-1.5">
                        <button
                          onClick={() => openEdit(user)}
                          className="p-2 hover:bg-slate-100 rounded-lg text-slate-500 hover:text-slate-800 transition cursor-pointer"
                          title="Edit User Details"
                        >
                          <Edit2 size={13} />
                        </button>
                        <button
                          onClick={() => openReset(user)}
                          className="p-2 hover:bg-slate-100 rounded-lg text-slate-500 hover:text-slate-800 transition cursor-pointer"
                          title="Reset User Password"
                        >
                          <Lock size={13} />
                        </button>
                        {user.is_active && (
                          <button
                            onClick={() => handleDeactivate(user)}
                            className="p-2 hover:bg-red-50 rounded-lg text-slate-400 hover:text-red-650 transition cursor-pointer"
                            title="Soft-Delete/Deactivate User"
                          >
                            <Trash2 size={13} />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5" className="py-16 text-center">
                    <ShieldAlert size={36} className="mx-auto text-slate-350 mb-2" />
                    <h4 className="font-bold text-slate-600 text-sm">No Accounts Found</h4>
                    <p className="text-xs text-slate-400 mt-1">No matches found in directory database.</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Footer pagination */}
        {totalPages > 1 && (
          <div className="border-t border-slate-100 px-6 py-4 bg-slate-50/50 flex items-center justify-between">
            <span className="text-[10px] font-extrabold uppercase text-slate-400 tracking-wider">
              Showing page {page} of {totalPages}
            </span>
            <div className="flex gap-2">
              <button
                disabled={page === 1}
                onClick={() => setPage(prev => Math.max(1, prev - 1))}
                className="p-1.5 rounded-lg bg-white border border-slate-200 disabled:opacity-50 text-slate-600 transition hover:bg-slate-50 cursor-pointer"
              >
                <ChevronLeft size={14} />
              </button>
              <button
                disabled={page === totalPages}
                onClick={() => setPage(prev => Math.min(totalPages, prev + 1))}
                className="p-1.5 rounded-lg bg-white border border-slate-200 disabled:opacity-50 text-slate-600 transition hover:bg-slate-50 cursor-pointer"
              >
                <ChevronRight size={14} />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Modal Dialogs */}
      <AnimatePresence>
        {/* ADD MODAL */}
        {addOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center">
            <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setAddOpen(false)} />
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="relative w-full max-w-md rounded-2xl bg-white p-6 border border-slate-200 shadow-2xl z-10 space-y-6"
            >
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <h3 className="text-lg font-black text-slate-800">Add New User</h3>
                <button onClick={() => setAddOpen(false)} className="p-1 text-slate-400 hover:text-slate-600 hover:bg-slate-50 rounded-lg cursor-pointer">
                  <X size={18} />
                </button>
              </div>

              {error && (
                <div className="alert-clinical-danger">
                  <ShieldAlert size={16} className="shrink-0 mt-0.5" />
                  <span>{error}</span>
                </div>
              )}

              <form onSubmit={handleCreate} className="space-y-4 text-xs font-semibold text-slate-500">
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black uppercase text-slate-400 tracking-wider">Username</label>
                  <input
                    type="text"
                    required
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="Enter unique username"
                    className="input-clinical"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black uppercase text-slate-400 tracking-wider">Email Address</label>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="user@intelliicu.org"
                    className="input-clinical"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black uppercase text-slate-400 tracking-wider">Secret Password</label>
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Minimum 6 characters"
                    className="input-clinical"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-[10px] font-black uppercase text-slate-400 tracking-wider">Security Role</label>
                    <select
                      required
                      value={role}
                      onChange={(e) => setRole(e.target.value)}
                      className="input-clinical font-bold"
                    >
                      <option value="">Select Role</option>
                      {roles.map(r => <option key={r.id} value={r.name}>{r.name}</option>)}
                    </select>
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-[10px] font-black uppercase text-slate-400 tracking-wider">Department</label>
                    <select
                      value={department}
                      onChange={(e) => setDepartment(e.target.value)}
                      className="input-clinical font-bold"
                    >
                      <option value="">None</option>
                      {departments.map(d => <option key={d.id} value={d.name}>{d.name}</option>)}
                    </select>
                  </div>
                </div>

                <div className="pt-4 border-t border-slate-100 flex gap-3">
                  <button
                    type="button"
                    onClick={() => setAddOpen(false)}
                    className="btn-clinical-secondary flex-1"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn-clinical-primary flex-1"
                  >
                    Create User
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}

        {/* EDIT MODAL */}
        {editOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center">
            <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setEditOpen(false)} />
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="relative w-full max-w-md rounded-2xl bg-white p-6 border border-slate-200 shadow-2xl z-10 space-y-6"
            >
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <h3 className="text-lg font-black text-slate-800">Edit User Account</h3>
                <button onClick={() => setEditOpen(false)} className="p-1 text-slate-400 hover:text-slate-600 hover:bg-slate-50 rounded-lg cursor-pointer">
                  <X size={18} />
                </button>
              </div>

              {error && (
                <div className="alert-clinical-danger">
                  <ShieldAlert size={16} className="shrink-0 mt-0.5" />
                  <span>{error}</span>
                </div>
              )}

              <form onSubmit={handleUpdate} className="space-y-4 text-xs font-semibold text-slate-500">
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black uppercase text-slate-400 tracking-wider">Username (Immutable)</label>
                  <input
                    type="text"
                    disabled
                    value={selectedUser?.username}
                    className="input-clinical bg-slate-100 opacity-60 cursor-not-allowed"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black uppercase text-slate-400 tracking-wider">Email Address</label>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="input-clinical"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-[10px] font-black uppercase text-slate-400 tracking-wider">Security Role</label>
                    <select
                      required
                      value={role}
                      onChange={(e) => setRole(e.target.value)}
                      className="input-clinical font-bold"
                    >
                      {roles.map(r => <option key={r.id} value={r.name}>{r.name}</option>)}
                    </select>
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-[10px] font-black uppercase text-slate-400 tracking-wider">Department</label>
                    <select
                      value={department}
                      onChange={(e) => setDepartment(e.target.value)}
                      className="input-clinical font-bold"
                    >
                      <option value="">None</option>
                      {departments.map(d => <option key={d.id} value={d.name}>{d.name}</option>)}
                    </select>
                  </div>
                </div>

                <div className="flex items-center justify-between p-3 bg-slate-50/50 rounded-xl border border-slate-100">
                  <div>
                    <label className="text-[10px] font-black uppercase text-slate-500 tracking-wider">Account Active Status</label>
                    <p className="text-[10px] text-slate-400 mt-0.5">Toggle to suspend or resume user access</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={isActive}
                    onChange={(e) => setIsActive(e.target.checked)}
                    className="h-4.5 w-4.5 rounded text-indigo-600 outline-none border-slate-200 transition cursor-pointer"
                  />
                </div>

                <div className="pt-4 border-t border-slate-100 flex gap-3">
                  <button
                    type="button"
                    onClick={() => setEditOpen(false)}
                    className="btn-clinical-secondary flex-1"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn-clinical-primary flex-1"
                  >
                    Save Changes
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}

        {/* RESET MODAL */}
        {resetOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center">
            <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setResetOpen(false)} />
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="relative w-full max-w-md rounded-2xl bg-white p-7 border border-slate-200 shadow-2xl z-10 space-y-6"
            >
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <h3 className="text-lg font-black text-slate-800 flex items-center gap-2">
                  <Lock size={18} className="text-slate-600" />
                  Reset User Password
                </h3>
                <button onClick={() => setResetOpen(false)} className="p-1 text-slate-400 hover:text-slate-600 hover:bg-slate-50 rounded-lg cursor-pointer">
                  <X size={18} />
                </button>
              </div>

              {error && (
                <div className="alert-clinical-danger">
                  <ShieldAlert size={16} className="shrink-0 mt-0.5" />
                  <span>{error}</span>
                </div>
              )}

              <form onSubmit={handleResetPassword} className="space-y-4 text-xs font-semibold text-slate-500">
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black uppercase text-slate-400 tracking-wider">Account Username</label>
                  <input
                    type="text"
                    disabled
                    value={selectedUser?.username}
                    className="input-clinical bg-slate-105 opacity-60 cursor-not-allowed"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black uppercase text-slate-400 tracking-wider">New Password</label>
                  <input
                    type="password"
                    required
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="Minimum 6 characters"
                    className="input-clinical"
                  />
                </div>

                <div className="pt-4 border-t border-slate-100 flex gap-3">
                  <button
                    type="button"
                    onClick={() => setResetOpen(false)}
                    className="btn-clinical-secondary flex-1"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn-clinical-primary flex-1"
                  >
                    Reset Password
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
