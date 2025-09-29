"use client";

import React, {useState} from "react";
import {StatusCodes} from "@/utils/statuscodes";
import {useRouter} from "next/navigation";

interface LoginResponse {
    access_token: string,
    refresh_token: string
}

export default function Login() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState<string | null>(null)
    const router = useRouter()

    const handleSubmit = async (e: React.FormEvent) => {
        setError(null) //Reset error state
        e.preventDefault()
        try {
            const response = await fetch("http://localhost:8000/auth/token", {
                method: "POST",
                headers: {"Content-Type": "application/x-www-form-urlencoded"},
                body: new URLSearchParams({
                    'username': username,
                    "password": password,
                    "scope": "",
                    "client_id": "",
                    "client_secret": ""
                })
            })
            if(!response.ok) {
                let detail = "Unknown error"
                try {
                    const errData = await response.json()
                    if(errData.detail) detail = errData.detail
                } catch {
                    // If response is not JSON
                    detail = response.statusText
                }
                if(response.status == StatusCodes.UNAUTHORIZED) {
                    setError("Incorrect username or password")
                } else {
                    setError(`Login failed: ${detail}`)
                }
                return
            }
            const data: LoginResponse = await response.json()
            localStorage.setItem("social_media_tokens", JSON.stringify(data))

            //Redirects the user to frontpage
            router.push('/')
        } catch (err) {
            setError("Server error — please try again later.")
            console.error("Network/Server error: ", err)
        }
    };
    return (
        <main>
            <div className="flex justify-center items-center min-h-screen">
                <div className="w-full max-w-md bg-white rounded-2xl shadow-lg p-8">
                    <h2 className="text-2xl font-bold text-center mb-6">Login</h2>
                    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Username</label>
                            <input
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-green-600 focus:border-green-600 sm:text-sm"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Password</label>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-green-600 focus:border-green-600 sm:text-sm"
                                required/>
                        </div>
                        <button type="submit"
                                className="w-full py-2 px-4 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 transition-colors">
                            Login
                        </button>
                    </form>
                    {error && <p className="text-red-500 mt-2">{error}</p>}
                </div>
            </div>
        </main>
    );
}
