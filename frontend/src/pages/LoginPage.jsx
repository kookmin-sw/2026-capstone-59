export default function LoginPage() {
  function handleLogin(provider) {
    window.location.href =
`/api/auth/${provider}/login`
  }

  return (
    <div>
      <h1>시작하기</h1>
      <button onClick={() => handleLogin('kakao')}>Kakao로 시작하기</button>
      <button onClick={() => handleLogin('google')}>Google로 시작하기</button>
      <button onClick={() => handleLogin('naver')}>Naver로 시작하기</button>
    </div>
  )
}