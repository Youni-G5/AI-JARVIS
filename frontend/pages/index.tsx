import Head from 'next/head'
import { useEffect, useState } from 'react'

export default function Home() {
  const [status, setStatus] = useState<string>('connecting...')
  const [services, setServices] = useState<any>({})

  useEffect(() => {
    // Check orchestrator health
    fetch(process.env.NEXT_PUBLIC_API_URL + '/health')
      .then(res => res.json())
      .then(data => {
        setStatus('connected')
        console.log('Orchestrator health:', data)
      })
      .catch(err => {
        setStatus('disconnected')
        console.error('Health check failed:', err)
      })
  }, [])

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <Head>
        <title>AI-JARVIS Dashboard</title>
        <meta name="description" content="AI-JARVIS Control Dashboard" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="container mx-auto p-8">
        <div className="text-center mb-12">
          <h1 className="text-6xl font-bold mb-4">🤖 AI-JARVIS</h1>
          <p className="text-xl text-gray-400">Autonomous AI Assistant Dashboard</p>
          <div className="mt-4">
            <span className={`px-4 py-2 rounded-full ${
              status === 'connected' ? 'bg-green-600' : 'bg-red-600'
            }`}>
              {status === 'connected' ? '✓ Connected' : '✗ Disconnected'}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <ServiceCard 
            title="Speech-to-Text"
            icon="🎤"
            port="8001"
            status="operational"
          />
          
          <ServiceCard 
            title="Text-to-Speech"
            icon="🗣️"
            port="8002"
            status="operational"
          />
          
          <ServiceCard 
            title="LLM Agent"
            icon="🧠"
            port="8003"
            status="operational"
          />
          
          <ServiceCard 
            title="Vision Service"
            icon="👁️"
            port="8004"
            status="operational"
          />
          
          <ServiceCard 
            title="Action Executor"
            icon="⚡"
            port="8006"
            status="operational"
          />
          
          <ServiceCard 
            title="Orchestrator"
            icon="🎯"
            port="8000"
            status="operational"
          />
        </div>

        <div className="mt-12 p-6 bg-gray-800 rounded-lg">
          <h2 className="text-2xl font-bold mb-4">Quick Actions</h2>
          <div className="grid grid-cols-2 gap-4">
            <button className="bg-blue-600 hover:bg-blue-700 p-4 rounded-lg">
              🎤 Voice Input
            </button>
            <button className="bg-purple-600 hover:bg-purple-700 p-4 rounded-lg">
              👁️ Vision Analysis
            </button>
            <button className="bg-green-600 hover:bg-green-700 p-4 rounded-lg">
              💬 Text Chat
            </button>
            <button className="bg-orange-600 hover:bg-orange-700 p-4 rounded-lg">
              ⚙️ Settings
            </button>
          </div>
        </div>

        <div className="mt-8 text-center text-gray-500">
          <p>AI-JARVIS v1.0.0 | Production-grade Autonomous AI Assistant</p>
          <p className="mt-2">Made with ❤️ for the AI community</p>
        </div>
      </main>
    </div>
  )
}

function ServiceCard({ title, icon, port, status }: any) {
  return (
    <div className="bg-gray-800 p-6 rounded-lg hover:bg-gray-700 transition">
      <div className="text-4xl mb-2">{icon}</div>
      <h3 className="text-xl font-bold mb-2">{title}</h3>
      <p className="text-gray-400 text-sm mb-2">Port: {port}</p>
      <span className="text-green-400 text-sm">● {status}</span>
    </div>
  )
}