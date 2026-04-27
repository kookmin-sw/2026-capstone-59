import { useNavigate } from 'react-router-dom'

export default function LandingPage() {
  const navigate = useNavigate()

  return (
    <div>
      <p>Your AI Development Partner</p>
      <h1>poco</h1>
      <button onClick={() => navigate('/login')}>Get started!</button>
    </div>
  )
}