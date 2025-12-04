// API client for calling FastAPI backend
// As specified in instructions.md

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface TimeSlot {
  id: string
  start_time: string
  end_time: string
  available: boolean
}

export interface BookingRequest {
  name: string
  email: string
  slot_id: string
}

export interface BookingResponse {
  success: boolean
  session_id: string
  message: string
}

export interface ActiveSession {
  session_id: string
  user_email: string
  start_time: string
  end_time: string
}

export interface SessionDetails {
  session_id: string
  user_name: string
  user_email: string
  start_time: string
  end_time: string
  status: string
}

class APIClient {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Unable to connect to the booking system. Please check your internet connection.')
      }
      throw error
    }
  }

  // Get available time slots for next 24 hours
  async getSlots(): Promise<{ slots: TimeSlot[] }> {
    return this.request<{ slots: TimeSlot[] }>('/api/slots')
  }

  // Create a new booking
  async createBooking(booking: BookingRequest): Promise<BookingResponse> {
    return this.request<BookingResponse>('/api/bookings', {
      method: 'POST',
      body: JSON.stringify(booking),
    })
  }

  // Get current active session
  async getActiveSession(): Promise<ActiveSession | null> {
    return this.request<ActiveSession | null>('/api/sessions/active')
  }

  // Get session details by ID
  async getSessionDetails(sessionId: string): Promise<SessionDetails> {
    return this.request<SessionDetails>(`/api/sessions/${sessionId}`)
  }
}

// Export singleton instance
export const apiClient = new APIClient()

// Export bound methods for convenience (preserving 'this' context)
export const getSlots = apiClient.getSlots.bind(apiClient)
export const createBooking = apiClient.createBooking.bind(apiClient)
export const getActiveSession = apiClient.getActiveSession.bind(apiClient)
export const getSessionDetails = apiClient.getSessionDetails.bind(apiClient)