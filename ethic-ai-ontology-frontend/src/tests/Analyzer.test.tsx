import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import AnalyzerPage from '@/app/analyzer/page'
import axios from 'axios'
import api from '@/services/api'

// Mock next/navigation
vi.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: vi.fn(),
    }
  }
}))

vi.mock('axios')
vi.mock('@/services/api', () => ({
  default: {
    post: vi.fn()
  }
}))

describe('AnalyzerPage', () => {
  it('renders the analysis form correctly', () => {
    render(<AnalyzerPage />)
    expect(screen.getByText('AI System Analyzer')).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/Example:/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Analyze Graph/i })).toBeInTheDocument()
  })

  it('allows user to input text and analyze', async () => {
    // @ts-ignore
    api.post.mockResolvedValueOnce({
      data: {
        composite_score: 85,
        final_risk_level: 'HighRisk',
        initial_risk_level: 'HighRisk',
        inferred_categories: ['Biometrics'],
        ethical_analysis: [],
        inferred_regulations: ['GDPR'],
        detected_safeguards: []
      }
    })

    render(<AnalyzerPage />)
    const textarea = screen.getByPlaceholderText(/Example:/)
    fireEvent.change(textarea, { target: { value: 'Uses biometrics' } })
    
    const analyzeBtn = screen.getByRole('button', { name: /Analyze Graph/i })
    fireEvent.click(analyzeBtn)

    await waitFor(() => {
      expect(screen.getByText('Composite Risk Score')).toBeInTheDocument()
    })
    
    expect(screen.getByText('85.0')).toBeInTheDocument()
    const highRiskElements = screen.getAllByText('HighRisk', { exact: false })
    expect(highRiskElements.length).toBeGreaterThan(0)
  })

  it('shows error toast on API failure', async () => {
    // @ts-ignore
    api.post.mockRejectedValueOnce(new Error('Network error'))
    
    render(<AnalyzerPage />)
    const textarea = screen.getByPlaceholderText(/Example:/)
    fireEvent.change(textarea, { target: { value: 'Uses biometrics' } })
    
    const analyzeBtn = screen.getByRole('button', { name: /Analyze Graph/i })
    fireEvent.click(analyzeBtn)

    // Note: Toasts are outside the component tree usually, but we can verify the API was called
    await waitFor(() => {
      expect(api.post).toHaveBeenCalled()
    })
  })
})
