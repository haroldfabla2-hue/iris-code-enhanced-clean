"""
TaskManager Component
Complete interface for Tasks API with 7 endpoints
"""

import React, { useState, useEffect } from 'react';
import { 
  PlayCircleIcon, 
  ClockIcon, 
  CheckCircleIcon, 
  XCircleIcon, 
  DocumentTextIcon,
  TrashIcon,
  PlusIcon,
  EyeIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import { useAppStore } from '../../stores/appStore';
import { mcpClient } from '../../lib/api';

interface Task {
  task_id: string;
  task_type: 'generation' | 'analysis' | 'processing' | 'automation';
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  created_at: string;
  progress?: number;
  estimated_duration?: number;
  parameters?: any;
  result?: any;
  error?: string;
}

interface CreateTaskForm {
  description: string;
  task_type: 'generation' | 'analysis' | 'processing' | 'automation';
  parameters: any;
}

const TaskManager: React.FC = () => {
  const { isConnected } = useAppStore();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [createForm, setCreateForm] = useState<CreateTaskForm>({
    description: '',
    task_type: 'generation',
    parameters: {}
  });
  const [filter, setFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'created_at' | 'status' | 'task_type'>('created_at');

  useEffect(() => {
    if (isConnected) {
      loadTasks();
      // Poll for task updates every 5 seconds
      const interval = setInterval(loadTasks, 5000);
      return () => clearInterval(interval);
    }
  }, [isConnected]);

  const loadTasks = async () => {
    if (!isConnected) return;
    
    setIsLoading(true);
    try {
      const response = await mcpClient.listTasks();
      if (response && response.tasks) {
        setTasks(response.tasks);
      }
    } catch (error) {
      console.error('Error loading tasks:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const createTask = async () => {
    if (!createForm.description.trim() || !isConnected) return;
    
    setIsCreating(true);
    try {
      const response = await mcpClient.createTask({
        description: createForm.description,
        task_type: createForm.task_type,
        parameters: createForm.parameters
      });
      
      if (response) {
        // Add to tasks list
        setTasks(prev => [{
          task_id: response.task_id,
          task_type: createForm.task_type,
          description: createForm.description,
          status: 'pending',
          created_at: new Date().toISOString(),
          parameters: createForm.parameters
        }, ...prev]);
        
        // Reset form
        setCreateForm({
          description: '',
          task_type: 'generation',
          parameters: {}
        });
        setShowCreateForm(false);
      }
    } catch (error) {
      console.error('Error creating task:', error);
      alert('Error creating task. Please try again.');
    } finally {
      setIsCreating(false);
    }
  };

  const executeTask = async (taskId: string) => {
    if (!isConnected) return;
    
    try {
      const response = await mcpClient.executeTask(taskId);
      if (response && response.status === 'success') {
        // Update task status in local state
        setTasks(prev => prev.map(task => 
          task.task_id === taskId 
            ? { ...task, status: 'running', progress: 0 }
            : task
        ));
      }
    } catch (error) {
      console.error('Error executing task:', error);
      alert('Error executing task. Please try again.');
    }
  };

  const deleteTask = async (taskId: string) => {
    if (!isConnected || !confirm('Are you sure you want to delete this task?')) return;
    
    try {
      const success = await mcpClient.deleteTask(taskId);
      if (success) {
        setTasks(prev => prev.filter(task => task.task_id !== taskId));
        if (selectedTask?.task_id === taskId) {
          setSelectedTask(null);
        }
      }
    } catch (error) {
      console.error('Error deleting task:', error);
      alert('Error deleting task. Please try again.');
    }
  };

  const getTaskStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100';
      case 'running': return 'text-blue-600 bg-blue-100';
      case 'failed': return 'text-red-600 bg-red-100';
      case 'pending': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getTaskIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircleIcon className="w-5 h-5" />;
      case 'running': return <ArrowPathIcon className="w-5 h-5 animate-spin" />;
      case 'failed': return <XCircleIcon className="w-5 h-5" />;
      case 'pending': return <ClockIcon className="w-5 h-5" />;
      default: return <DocumentTextIcon className="w-5 h-5" />;
    }
  };

  const getTaskTypeColor = (type: string) => {
    switch (type) {
      case 'generation': return 'text-purple-600 bg-purple-100';
      case 'analysis': return 'text-indigo-600 bg-indigo-100';
      case 'processing': return 'text-orange-600 bg-orange-100';
      case 'automation': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const filteredTasks = tasks.filter(task => {
    if (filter === 'all') return true;
    return task.status === filter;
  });

  const sortedTasks = [...filteredTasks].sort((a, b) => {
    switch (sortBy) {
      case 'created_at':
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      case 'status':
        return a.status.localeCompare(b.status);
      case 'task_type':
        return a.task_type.localeCompare(b.task_type);
      default:
        return 0;
    }
  });

  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Task Manager</h1>
            <p className="text-gray-600 mt-1">
              Manage and monitor your AI tasks and workflows
            </p>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={loadTasks}
              disabled={isLoading}
              className="flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50"
            >
              <ArrowPathIcon className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
            <button
              onClick={() => setShowCreateForm(true)}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <PlusIcon className="w-4 h-4 mr-2" />
              New Task
            </button>
          </div>
        </div>
      </div>

      {/* Create Task Form Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Create New Task</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={createForm.description}
                  onChange={(e) => setCreateForm(prev => ({ ...prev, description: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={3}
                  placeholder="Describe what this task should do..."
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Task Type
                </label>
                <select
                  value={createForm.task_type}
                  onChange={(e) => setCreateForm(prev => ({ 
                    ...prev, 
                    task_type: e.target.value as any 
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="generation">Generation</option>
                  <option value="analysis">Analysis</option>
                  <option value="processing">Processing</option>
                  <option value="automation">Automation</option>
                </select>
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowCreateForm(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                Cancel
              </button>
              <button
                onClick={createTask}
                disabled={!createForm.description.trim() || isCreating}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {isCreating ? 'Creating...' : 'Create Task'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <DocumentTextIcon className="w-8 h-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Tasks</p>
              <p className="text-2xl font-semibold text-gray-900">{tasks.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <ClockIcon className="w-8 h-8 text-yellow-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Pending</p>
              <p className="text-2xl font-semibold text-gray-900">
                {tasks.filter(t => t.status === 'pending').length}
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <ArrowPathIcon className="w-8 h-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Running</p>
              <p className="text-2xl font-semibold text-gray-900">
                {tasks.filter(t => t.status === 'running').length}
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <CheckCircleIcon className="w-8 h-8 text-green-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Completed</p>
              <p className="text-2xl font-semibold text-gray-900">
                {tasks.filter(t => t.status === 'completed').length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters and Sort */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="flex flex-wrap items-center gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Filter by Status</label>
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Tasks</option>
              <option value="pending">Pending</option>
              <option value="running">Running</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Sort by</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="created_at">Creation Date</option>
              <option value="status">Status</option>
              <option value="task_type">Task Type</option>
            </select>
          </div>
        </div>
      </div>

      {/* Tasks List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center">
            <ArrowPathIcon className="w-8 h-8 animate-spin text-blue-600 mx-auto" />
            <p className="text-gray-600 mt-2">Loading tasks...</p>
          </div>
        ) : sortedTasks.length === 0 ? (
          <div className="p-8 text-center">
            <DocumentTextIcon className="w-12 h-12 text-gray-400 mx-auto" />
            <p className="text-gray-600 mt-2">No tasks found</p>
            <p className="text-gray-500 text-sm">Create your first task to get started</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Task
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {sortedTasks.map((task) => (
                  <tr key={task.task_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {task.description}
                        </div>
                        {task.progress !== undefined && (
                          <div className="mt-1">
                            <div className="bg-gray-200 rounded-full h-2">
                              <div
                                className="bg-blue-600 h-2 rounded-full"
                                style={{ width: `${task.progress}%` }}
                              />
                            </div>
                            <p className="text-xs text-gray-500 mt-1">
                              {task.progress}% complete
                            </p>
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getTaskTypeColor(task.task_type)}`}>
                        {task.task_type}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getTaskStatusColor(task.status)}`}>
                        {getTaskIcon(task.status)}
                        <span className="ml-1 capitalize">{task.status}</span>
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {new Date(task.created_at).toLocaleString()}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => setSelectedTask(task)}
                          className="text-blue-600 hover:text-blue-800"
                          title="View Details"
                        >
                          <EyeIcon className="w-4 h-4" />
                        </button>
                        
                        {task.status === 'pending' && (
                          <button
                            onClick={() => executeTask(task.task_id)}
                            className="text-green-600 hover:text-green-800"
                            title="Execute Task"
                          >
                            <PlayCircleIcon className="w-4 h-4" />
                          </button>
                        )}
                        
                        <button
                          onClick={() => deleteTask(task.task_id)}
                          className="text-red-600 hover:text-red-800"
                          title="Delete Task"
                        >
                          <TrashIcon className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Task Details Modal */}
      {selectedTask && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-lg font-semibold">Task Details</h3>
              <button
                onClick={() => setSelectedTask(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Description</label>
                <p className="text-gray-900">{selectedTask.description}</p>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Task ID</label>
                  <p className="text-gray-900 font-mono text-sm">{selectedTask.task_id}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Type</label>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getTaskTypeColor(selectedTask.task_type)}`}>
                    {selectedTask.task_type}
                  </span>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Status</label>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getTaskStatusColor(selectedTask.status)}`}>
                  {getTaskIcon(selectedTask.status)}
                  <span className="ml-1 capitalize">{selectedTask.status}</span>
                </span>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Created</label>
                <p className="text-gray-900">{new Date(selectedTask.created_at).toLocaleString()}</p>
              </div>
              
              {selectedTask.progress !== undefined && (
                <div>
                  <label className="block text-sm font-medium text-gray-700">Progress</label>
                  <div className="mt-1">
                    <div className="bg-gray-200 rounded-full h-4">
                      <div
                        className="bg-blue-600 h-4 rounded-full flex items-center justify-center"
                        style={{ width: `${selectedTask.progress}%` }}
                      >
                        <span className="text-white text-xs font-medium">{selectedTask.progress}%</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              {selectedTask.parameters && (
                <div>
                  <label className="block text-sm font-medium text-gray-700">Parameters</label>
                  <pre className="bg-gray-100 p-3 rounded text-sm overflow-x-auto">
                    {JSON.stringify(selectedTask.parameters, null, 2)}
                  </pre>
                </div>
              )}
              
              {selectedTask.result && (
                <div>
                  <label className="block text-sm font-medium text-gray-700">Result</label>
                  <pre className="bg-gray-100 p-3 rounded text-sm overflow-x-auto">
                    {JSON.stringify(selectedTask.result, null, 2)}
                  </pre>
                </div>
              )}
              
              {selectedTask.error && (
                <div>
                  <label className="block text-sm font-medium text-gray-700">Error</label>
                  <p className="text-red-600 text-sm">{selectedTask.error}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TaskManager;