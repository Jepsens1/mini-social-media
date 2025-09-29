"use client"

import React, {useState} from "react";
import {StatusCodes} from "@/utils/statuscodes";

export default function CreatePost() {
    const [title, setTitle] = useState('');
    const [content, setContent] = useState('');
    const [error, setError] = useState<string | null>(null);
    const handleSubmit = async (e: React.FormEvent) => {
        setError(null);
        e.preventDefault()
        try {
            const response = await fetch("http://localhost:8000/posts", {
                method: "POST",
                headers: {"Content-Type": "application/json", "Authorization": "Bearer " + localStorage.getItem("social_media_tokens")},
                body: JSON.stringify({title, content})
            })
            if (!response.ok) {
                let detail = "Unknown error"
                try {
                    const errData = await response.json();
                    if (errData.detail) detail = errData.detail;
                } catch {
                    // If response is not JSON
                    detail = response.statusText
                }
                if (response.status == StatusCodes.VALIDATION_ERROR) {
                    setError("Validation error")
                } else {
                    setError(`Create Post failed: ${detail}`)
                }
                return
            }
            const data = await response.json()
            console.log(data)
        } catch (err) {
            setError("Server error — please try again later.")
            console.error("Network/Server error: ", err)
        }
    }
    return (
        <main>
            <div className="flex justify-center min-h-screen">
                <div className="w-full max-w-md bg-white rounded-2xl shadow-lg p-8 m-3">
                    <h2 className="text-2xl font-bold text-center mb-6">Create Post</h2>
                    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Title</label>
                            <input type="text" value={title} required onChange={e => setTitle(e.target.value)}
                                   className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-green-600 focus:border-green-600 sm:text-sm"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Content</label>
                            <textarea rows={10} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-green-600 focus:border-green-600 sm:text-sm" value={content} placeholder="Write your content here..." onChange={e => setContent(e.target.value)}></textarea>
                        </div>
                        <button type="submit"
                                className="w-full py-2 px-4 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 transition-colors">
                            Create
                        </button>
                    </form>
                    {error && <p className="text-red-500 mt-2">{error}</p>}
                </div>
            </div>
        </main>
    )
}