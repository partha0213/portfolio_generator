'use client';

import { useState } from 'react';

interface ReviewDataProps {
    parsedData: any;
    confidence: any;
    onConfirm: (data: any) => void;
    onBack: () => void;
}

export default function ReviewData({ parsedData, confidence, onConfirm, onBack }: ReviewDataProps) {
    const [editableData, setEditableData] = useState(parsedData);
    const [errors, setErrors] = useState<Record<string, string>>({});

    const validateData = () => {
        const newErrors: Record<string, string> = {};
        if (!editableData.name?.trim()) newErrors.name = "Name is required";
        if (!editableData.email?.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) newErrors.email = "Invalid email format";
        return newErrors;
    };

    const handleConfirm = () => {
        const validationErrors = validateData();
        if (Object.keys(validationErrors).length === 0) {
            onConfirm(editableData);
        } else {
            setErrors(validationErrors);
        }
    };

    const getConfidenceIndicator = (field: string) => {
        const score = confidence?.[field];
        if (score !== undefined && score < 0.7) {
            return <span className="text-yellow-500 ml-2 cursor-help" title="Low confidence - please verify">⚠️</span>;
        }
        return null;
    };

    return (
        <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-3xl mx-auto bg-white rounded-xl shadow-lg overflow-hidden">
                <div className="px-8 py-6 border-b border-gray-200">
                    <h2 className="text-2xl font-bold text-gray-900">Review Your Information</h2>
                    <p className="mt-1 text-gray-500">Please verify the information we extracted from your resume</p>
                </div>

                <div className="px-8 py-6 space-y-8">
                    {/* Personal Info */}
                    <section>
                        <h3 className="text-lg font-medium text-gray-900 mb-4">Personal Information</h3>
                        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Name * {getConfidenceIndicator('name')}</label>
                                <input
                                    type="text"
                                    value={editableData.name || ''}
                                    onChange={(e) => setEditableData({ ...editableData, name: e.target.value })}
                                    className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border ${errors.name ? 'border-red-500' : ''}`}
                                />
                                {errors.name && <p className="mt-1 text-sm text-red-600">{errors.name}</p>}
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700">Email * {getConfidenceIndicator('email')}</label>
                                <input
                                    type="email"
                                    value={editableData.email || ''}
                                    onChange={(e) => setEditableData({ ...editableData, email: e.target.value })}
                                    className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border ${errors.email ? 'border-red-500' : ''}`}
                                />
                                {errors.email && <p className="mt-1 text-sm text-red-600">{errors.email}</p>}
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700">Phone</label>
                                <input
                                    type="text"
                                    value={editableData.phone || ''}
                                    onChange={(e) => setEditableData({ ...editableData, phone: e.target.value })}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700">Title/Role</label>
                                <input
                                    type="text"
                                    value={editableData.title || ''}
                                    onChange={(e) => setEditableData({ ...editableData, title: e.target.value })}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
                                />
                            </div>
                        </div>
                    </section>

                    {/* Skills */}
                    <section>
                        <h3 className="text-lg font-medium text-gray-900 mb-4">Skills {getConfidenceIndicator('skills')}</h3>
                        <div className="flex flex-wrap gap-2">
                            {editableData.skills?.map((skill: string, idx: number) => (
                                <div key={idx} className="flex items-center bg-gray-100 rounded-full px-3 py-1">
                                    <input
                                        value={skill}
                                        onChange={(e) => {
                                            const newSkills = [...editableData.skills];
                                            newSkills[idx] = e.target.value;
                                            setEditableData({ ...editableData, skills: newSkills });
                                        }}
                                        className="bg-transparent border-none focus:ring-0 text-sm w-24"
                                    />
                                    <button
                                        onClick={() => {
                                            const newSkills = editableData.skills.filter((_: any, i: number) => i !== idx);
                                            setEditableData({ ...editableData, skills: newSkills });
                                        }}
                                        className="ml-2 text-gray-400 hover:text-red-500"
                                    >
                                        ×
                                    </button>
                                </div>
                            ))}
                            <button
                                onClick={() => setEditableData({ ...editableData, skills: [...(editableData.skills || []), ''] })}
                                className="inline-flex items-center px-3 py-1 border border-gray-300 shadow-sm text-sm font-medium rounded-full text-gray-700 bg-white hover:bg-gray-50"
                            >
                                + Add Skill
                            </button>
                        </div>
                    </section>

                    {/* Projects */}
                    <section>
                        <h3 className="text-lg font-medium text-gray-900 mb-4">Projects {getConfidenceIndicator('projects')}</h3>
                        <div className="space-y-4">
                            {editableData.projects?.map((project: any, idx: number) => (
                                <div key={idx} className="border rounded-lg p-4 bg-gray-50 relative">
                                    <button
                                        onClick={() => {
                                            const newProjects = editableData.projects.filter((_: any, i: number) => i !== idx);
                                            setEditableData({ ...editableData, projects: newProjects });
                                        }}
                                        className="absolute top-2 right-2 text-gray-400 hover:text-red-500"
                                    >
                                        Remove
                                    </button>
                                    <div className="grid grid-cols-1 gap-4">
                                        <input
                                            placeholder="Project Name"
                                            value={project.name}
                                            onChange={(e) => {
                                                const newProjects = [...editableData.projects];
                                                newProjects[idx].name = e.target.value;
                                                setEditableData({ ...editableData, projects: newProjects });
                                            }}
                                            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
                                        />
                                        <textarea
                                            placeholder="Description"
                                            value={project.description}
                                            onChange={(e) => {
                                                const newProjects = [...editableData.projects];
                                                newProjects[idx].description = e.target.value;
                                                setEditableData({ ...editableData, projects: newProjects });
                                            }}
                                            rows={2}
                                            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
                                        />
                                    </div>
                                </div>
                            ))}
                            <button
                                onClick={() => setEditableData({
                                    ...editableData,
                                    projects: [...(editableData.projects || []), { name: '', description: '' }]
                                })}
                                className="w-full py-2 border-2 border-dashed border-gray-300 rounded-lg text-gray-500 hover:border-indigo-500 hover:text-indigo-500 transition-colors"
                            >
                                + Add Project
                            </button>
                        </div>
                    </section>

                    {/* Actions */}
                    <div className="flex justify-end space-x-4 pt-6 border-t border-gray-200">
                        <button
                            onClick={onBack}
                            className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                        >
                            Back
                        </button>
                        <button
                            onClick={handleConfirm}
                            className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                        >
                            Generate Portfolio
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
