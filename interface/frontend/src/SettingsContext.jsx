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
  // const [userComment, setUserComment] = useState('')

  return (
    <SettingsContext.Provider value={{ partnerTypeDefinitions, setPartnerTypeDefinitions }}>
      {children}
    </SettingsContext.Provider>
  )
}
