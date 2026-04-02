async function globalTeardown() {
  await fetch('http://localhost:8001/api/test/reset', { method: 'DELETE' })
}

export default globalTeardown
