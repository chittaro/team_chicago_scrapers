Hexagon Project Frontend UI Design Specification#OverviewThis document defines the user flow and interface layout for the Hexagon Project frontend. It mimics a clean, conversational style similar to ChatGPT, optimized for simplicity and live updates.
#UserFlow#HomepagePrompt: #PromptInput - Centered input field asking: "Enter a company name to find partnerships"
Action: User enters a company name and presses Enter.
#LiveURLScrapingDisplayResponse: #LiveUpdate - As the backend scraper finds URLs, each URL appears line-by-line underneath the input field.
Each URL row contains:
#URLText - URL text displayed
#RemoveButton - [X] button on the far right to remove unwanted URLs
Animation: URLs should fade in gently as they appear.
#PostURLCollectionActionsOnce all URLs are scraped and displayed:
Two buttons appear below the URL list:
[#AddAnotherURL]: Manually add more URLs.
[#ContinueButton]: Proceed to the next view.
#PartnershipsTableViewAfter pressing [#ContinueButton], a new chat bubble appears below, containing a table populated with partnership data from the SQL database.
#TableLayoutThe table should have the following columns:
Company NamePartnership NamePartnership TypeURL Scraped FromDate ScrapedStatus#SQLSchemaData should be pulled from:
CREATE TABLE partnerships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name TEXT NOT NULL,
    partnership_name TEXT NOT NULL,
    partnership_type TEXT,
    url_scraped_from TEXT,
    date_scraped TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'Pending'
);Each partnership entry must show:
#CompanyName
#PartnerName
#PartnershipType
#URLScrapedFrom
#DateScraped
#Status
#VisualStyleClean, minimalistic design
Light-gray page background
White chat bubble style cards
Subtle shadowing under bubbles and tables
TailwindCSS styling for fast, responsive design
#ComponentsToBuild#CompanyPromptInput.jsx
#LiveURLDisplay.jsx
#PartnershipsTable.jsx
#AddURLModal.jsx (optional enhancement)
#NotesUX must feel "alive" as URLs are being found.
Focus on smooth transitions and conversational UI.
Use React functional components with hooks (#useState, #useEffect).
Axios or fetch will be used to communicate with backend APIs.
End of Document