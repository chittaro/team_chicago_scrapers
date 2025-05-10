// src/SettingsContext.js
import { createContext, useState, useEffect, useCallback } from 'react'

export const SettingsContext = createContext()

const API_BASE_URL = 'http://127.0.0.1:5000/api/settings' // Your backend URL

export function SettingsProvider({ children }) {
  const [categorySettings, setCategorySettings] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  // Fetch all category settings on mount
  const fetchCategorySettings = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await fetch(API_BASE_URL)
      if (!response.ok) {
        const errData = await response.json().catch(() => ({})) // Try to get error body
        throw new Error(errData.error || `HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      setCategorySettings(data || []) // Ensure it's an array
    } catch (e) {
      console.error("Failed to fetch category settings:", e)
      setError(e.message)
      setCategorySettings([]) // Set to empty array on error
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchCategorySettings()
  }, [fetchCategorySettings])

  // Function to add a new partner type/category
  const addCategory = async (name, definition = '', is_enabled = true) => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_BASE_URL}/category`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, definition, is_enabled }),
      })
      if (!response.ok) {
        const errData = await response.json().catch(() => ({}))
        throw new Error(errData.error || `HTTP error! status: ${response.status}`)
      }
      const newCategory = await response.json()
      // Add to local state (could also refetch all settings for absolute consistency)
      setCategorySettings(prev => [...prev, newCategory]) 
      return newCategory;
    } catch (e) {
      console.error("Failed to add category:", e)
      setError(e.message)
      throw e; // Re-throw to allow component to handle
    } finally {
      setIsLoading(false)
    }
  }

  // Function to update a category's setting (definition or is_enabled)
  const updateSetting = async (setting_id, definition, is_enabled) => {
    setIsLoading(true)
    setError(null)
    const payload = {}
    // Only include fields if they are not undefined, to allow selective updates
    if (definition !== undefined) payload.definition = definition
    if (is_enabled !== undefined) payload.is_enabled = is_enabled

    if (Object.keys(payload).length === 0) {
      // Nothing to update
      setIsLoading(false);
      return categorySettings.find(s => s.setting_id === setting_id); // Return current setting
    }

    try {
      const response = await fetch(`${API_BASE_URL}/category_setting/${setting_id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })
      if (!response.ok) {
        const errData = await response.json().catch(() => ({}))
        throw new Error(errData.error || `HTTP error! status: ${response.status}`)
      }
      const updatedSetting = await response.json()
      // Update local state
      setCategorySettings(prev => 
        prev.map(s => s.setting_id === setting_id ? { ...s, ...updatedSetting } : s)
      )
      return updatedSetting;
    } catch (e) {
      console.error("Failed to update setting:", e)
      setError(e.message)
      throw e;
    } finally {
      setIsLoading(false)
    }
  }

  // Function to remove a partner type/category
  const deleteCategory = async (category_id) => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_BASE_URL}/category/${category_id}`, {
        method: 'DELETE',
      })
      if (!response.ok) {
        const errData = await response.json().catch(() => ({}))
        throw new Error(errData.error || `HTTP error! status: ${response.status}`)
      }
      // Remove from local state
      setCategorySettings(prev => prev.filter(s => s.id !== category_id))
      return true; // Indicate success
    } catch (e) {
      console.error("Failed to delete category:", e)
      setError(e.message)
      throw e;
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <SettingsContext.Provider value={{
      categorySettings, // This will be an array of {id, name, definition, is_enabled, setting_id}
      isLoading,
      error,
      fetchCategorySettings, // Expose to allow manual refresh if needed
      addCategory,
      updateSetting,
      deleteCategory
    }}>
      {children}
    </SettingsContext.Provider>
  )
}
