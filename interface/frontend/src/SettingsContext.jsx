// src/SettingsContext.js
import { createContext, useState } from 'react'

export const SettingsContext = createContext()

export function SettingsProvider({ children }) {
  const [partnerTypeDefinitions, setPartnerTypeDefinitions] = useState({
    "Strategic Partner": '',
    "Software Partner": '',
    "Hardware Partner": '',
    "HPC Partner": '',
    "Reseller": '',
  })
  
  // By default, all partner types are enabled
  const [enabledPartnerTypes, setEnabledPartnerTypes] = useState([
    "Strategic Partner", 
    "Software Partner", 
    "Hardware Partner", 
    "HPC Partner", 
    "Reseller"
  ])

  // Add a new partner type
  const addPartnerType = (newType) => {
    // Add to definitions
    setPartnerTypeDefinitions(prev => ({
      ...prev,
      [newType]: ''
    }))
    
    // Enable it by default
    setEnabledPartnerTypes(prev => [...prev, newType])
  }

  // Remove a partner type
  const removePartnerType = (typeToRemove) => {
    // Remove from definitions
    setPartnerTypeDefinitions(prev => {
      const newDefs = {...prev}
      delete newDefs[typeToRemove]
      return newDefs
    })
    
    // Remove from enabled types
    setEnabledPartnerTypes(prev => 
      prev.filter(type => type !== typeToRemove)
    )
  }

  return (
    <SettingsContext.Provider value={{ 
      partnerTypeDefinitions, 
      setPartnerTypeDefinitions,
      enabledPartnerTypes,
      setEnabledPartnerTypes,
      addPartnerType,
      removePartnerType
    }}>
      {children}
    </SettingsContext.Provider>
  )
}
