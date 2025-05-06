import { Link } from 'react-router-dom'

function Settings() {
  return (
    <div className="min-h-screen bg-gray-100 py-8 px-4">
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold mb-4">Prompt Settings</h2>
        <p className="mb-4">Here you can adjust your application preferences.</p>

        <Link to="/" className="text-blue-500 hover:underline">
          ← Back to Main
        </Link>
      </div>
    </div>
  )
}

export default Settings