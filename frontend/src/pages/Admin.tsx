/**
 * Admin Dashboard - Database management interface
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import {
  Users,
  FileText,
  Shield,
  Trash2,
  UserCheck,
  UserX,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Database,
  Activity,
  TrendingUp
} from 'lucide-react';

interface AdminStats {
  total_users: number;
  total_reports: number;
  active_users: number;
  admin_users: number;
  avg_security_score: number;
  avg_maintainability_score: number;
  avg_architecture_score: number;
  reports_today: number;
}

interface User {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
}

interface Report {
  id: number;
  user_id: number;
  repo_url: string;
  repo_name: string;
  branch: string;
  security_score: number;
  maintainability_score: number;
  architecture_score: number;
  tech_debt_index: number;
  refactor_urgency: string;
  files_analyzed: number;
  total_lines: number;
  analysis_duration_seconds: number;
  created_at: string;
  username?: string;
}

const Admin: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'reports'>('overview');
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<number | null>(null);

  useEffect(() => {
    if (!user?.is_admin) {
      navigate('/dashboard');
      return;
    }
    fetchData();
  }, [user, navigate]);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsRes, usersRes, reportsRes] = await Promise.all([
        api.get('/admin/stats'),
        api.get('/admin/users'),
        api.get('/admin/reports')
      ]);
      setStats(statsRes.data);
      setUsers(usersRes.data);
      setReports(reportsRes.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load admin data');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleAdmin = async (userId: number) => {
    setActionLoading(userId);
    try {
      await api.post(`/admin/users/${userId}/toggle-admin`);
      await fetchData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to update user');
    } finally {
      setActionLoading(null);
    }
  };

  const handleDeleteUser = async (userId: number, username: string) => {
    if (!confirm(`Are you sure you want to delete user "${username}" and all their reports?`)) {
      return;
    }
    setActionLoading(userId);
    try {
      await api.delete(`/admin/users/${userId}`);
      await fetchData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete user');
    } finally {
      setActionLoading(null);
    }
  };

  const handleDeleteReport = async (reportId: number) => {
    if (!confirm('Are you sure you want to delete this report?')) {
      return;
    }
    setActionLoading(reportId);
    try {
      await api.delete(`/admin/reports/${reportId}`);
      await fetchData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete report');
    } finally {
      setActionLoading(null);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    if (score >= 40) return 'text-orange-400';
    return 'text-red-400';
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency.toLowerCase()) {
      case 'low': return 'bg-green-500/20 text-green-400';
      case 'medium': return 'bg-yellow-500/20 text-yellow-400';
      case 'high': return 'bg-orange-500/20 text-orange-400';
      case 'critical': return 'bg-red-500/20 text-red-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-dark-950 pt-20 flex items-center justify-center">
        <div className="flex items-center gap-3 text-gray-400">
          <RefreshCw className="w-6 h-6 animate-spin" />
          <span>Loading admin dashboard...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-dark-950 pt-20 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <p className="text-red-400">{error}</p>
          <button onClick={fetchData} className="mt-4 btn-glow">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-dark-950 pt-20 pb-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center gap-3">
              <Database className="w-8 h-8 text-primary-500" />
              Admin Dashboard
            </h1>
            <p className="text-gray-400 mt-1">Manage users and analysis reports</p>
          </div>
          <button
            onClick={fetchData}
            className="flex items-center gap-2 px-4 py-2 bg-dark-800 hover:bg-dark-700
                     text-gray-300 rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-dark-800">
          {[
            { id: 'overview', label: 'Overview', icon: Activity },
            { id: 'users', label: 'Users', icon: Users },
            { id: 'reports', label: 'Reports', icon: FileText }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-primary-500 text-primary-400'
                  : 'border-transparent text-gray-400 hover:text-white'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && stats && (
          <div className="space-y-6">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="glass-card p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Total Users</p>
                    <p className="text-3xl font-bold text-white mt-1">{stats.total_users}</p>
                  </div>
                  <Users className="w-10 h-10 text-primary-500 opacity-50" />
                </div>
                <p className="text-sm text-gray-500 mt-2">
                  {stats.active_users} active, {stats.admin_users} admins
                </p>
              </div>

              <div className="glass-card p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Total Reports</p>
                    <p className="text-3xl font-bold text-white mt-1">{stats.total_reports}</p>
                  </div>
                  <FileText className="w-10 h-10 text-blue-500 opacity-50" />
                </div>
                <p className="text-sm text-gray-500 mt-2">
                  {stats.reports_today} today
                </p>
              </div>

              <div className="glass-card p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Avg Security Score</p>
                    <p className={`text-3xl font-bold mt-1 ${getScoreColor(stats.avg_security_score)}`}>
                      {stats.avg_security_score}
                    </p>
                  </div>
                  <Shield className="w-10 h-10 text-green-500 opacity-50" />
                </div>
              </div>

              <div className="glass-card p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Avg Maintainability</p>
                    <p className={`text-3xl font-bold mt-1 ${getScoreColor(stats.avg_maintainability_score)}`}>
                      {stats.avg_maintainability_score}
                    </p>
                  </div>
                  <TrendingUp className="w-10 h-10 text-yellow-500 opacity-50" />
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="glass-card p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Recent Reports</h3>
              <div className="space-y-3">
                {reports.slice(0, 5).map((report) => (
                  <div key={report.id} className="flex items-center justify-between py-2 border-b border-dark-700 last:border-0">
                    <div>
                      <p className="text-white font-medium">{report.repo_name}</p>
                      <p className="text-sm text-gray-400">by {report.username} - {new Date(report.created_at).toLocaleDateString()}</p>
                    </div>
                    <span className={`px-2 py-1 rounded text-xs ${getUrgencyColor(report.refactor_urgency)}`}>
                      {report.refactor_urgency}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Users Tab */}
        {activeTab === 'users' && (
          <div className="glass-card overflow-hidden">
            <table className="w-full">
              <thead className="bg-dark-800">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Username</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Email</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Role</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Created</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-dark-700">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-dark-800/50">
                    <td className="px-6 py-4 text-sm text-gray-300">{u.id}</td>
                    <td className="px-6 py-4 text-sm text-white font-medium">{u.username}</td>
                    <td className="px-6 py-4 text-sm text-gray-300">{u.email}</td>
                    <td className="px-6 py-4">
                      {u.is_active ? (
                        <span className="flex items-center gap-1 text-green-400 text-sm">
                          <CheckCircle className="w-4 h-4" /> Active
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 text-red-400 text-sm">
                          <XCircle className="w-4 h-4" /> Inactive
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 rounded text-xs ${
                        u.is_admin ? 'bg-primary-500/20 text-primary-400' : 'bg-gray-500/20 text-gray-400'
                      }`}>
                        {u.is_admin ? 'Admin' : 'User'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-400">
                      {new Date(u.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleToggleAdmin(u.id)}
                          disabled={actionLoading === u.id || u.id === user?.id}
                          className={`p-2 rounded transition-colors ${
                            u.id === user?.id
                              ? 'text-gray-600 cursor-not-allowed'
                              : u.is_admin
                              ? 'text-yellow-400 hover:bg-yellow-500/20'
                              : 'text-green-400 hover:bg-green-500/20'
                          }`}
                          title={u.is_admin ? 'Remove admin' : 'Make admin'}
                        >
                          {u.is_admin ? <UserX className="w-4 h-4" /> : <UserCheck className="w-4 h-4" />}
                        </button>
                        <button
                          onClick={() => handleDeleteUser(u.id, u.username)}
                          disabled={actionLoading === u.id || u.id === user?.id}
                          className={`p-2 rounded transition-colors ${
                            u.id === user?.id
                              ? 'text-gray-600 cursor-not-allowed'
                              : 'text-red-400 hover:bg-red-500/20'
                          }`}
                          title="Delete user"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Reports Tab */}
        {activeTab === 'reports' && (
          <div className="glass-card overflow-hidden">
            <table className="w-full">
              <thead className="bg-dark-800">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">ID</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Repository</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">User</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Security</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Maintain</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Arch</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Debt</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Urgency</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Date</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-dark-700">
                {reports.map((r) => (
                  <tr key={r.id} className="hover:bg-dark-800/50">
                    <td className="px-4 py-4 text-sm text-gray-300">{r.id}</td>
                    <td className="px-4 py-4 text-sm text-white font-medium">{r.repo_name}</td>
                    <td className="px-4 py-4 text-sm text-gray-300">{r.username}</td>
                    <td className={`px-4 py-4 text-sm font-medium ${getScoreColor(r.security_score)}`}>
                      {r.security_score.toFixed(1)}
                    </td>
                    <td className={`px-4 py-4 text-sm font-medium ${getScoreColor(r.maintainability_score)}`}>
                      {r.maintainability_score.toFixed(1)}
                    </td>
                    <td className={`px-4 py-4 text-sm font-medium ${getScoreColor(r.architecture_score)}`}>
                      {r.architecture_score.toFixed(1)}
                    </td>
                    <td className="px-4 py-4 text-sm text-gray-300">{r.tech_debt_index.toFixed(1)}</td>
                    <td className="px-4 py-4">
                      <span className={`px-2 py-1 rounded text-xs ${getUrgencyColor(r.refactor_urgency)}`}>
                        {r.refactor_urgency}
                      </span>
                    </td>
                    <td className="px-4 py-4 text-sm text-gray-400">
                      {new Date(r.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-4">
                      <button
                        onClick={() => handleDeleteReport(r.id)}
                        disabled={actionLoading === r.id}
                        className="p-2 text-red-400 hover:bg-red-500/20 rounded transition-colors"
                        title="Delete report"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Admin;
