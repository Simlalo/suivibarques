# PowerShell Script to Remove Unused UI Components
# This script removes all shadcn/ui components that are not used in your dashboard app

# Set error action preference
$ErrorActionPreference = "Continue"

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Cleaning Unused UI Components" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Define the path to the UI components directory
$uiComponentsPath = "src\components\ui"

# Check if we're in the right directory
if (-not (Test-Path $uiComponentsPath)) {
    Write-Host "ERROR: Not in the client directory. Please run this from the 'client' folder." -ForegroundColor Red
    Write-Host "Current location: $(Get-Location)" -ForegroundColor Yellow
    exit 1
}

# Components ACTUALLY USED in your dashboard (based on dashboard.tsx analysis)
$usedComponents = @(
    "button.tsx",
    "card.tsx",
    "input.tsx",
    "select.tsx",
    "badge.tsx",
    "toast.tsx",
    "toaster.tsx",
    "sonner.tsx",
    "tooltip.tsx",
    "label.tsx"
)

# Get all component files
$allComponents = Get-ChildItem -Path $uiComponentsPath -Filter "*.tsx" | Select-Object -ExpandProperty Name

Write-Host "Found $($allComponents.Count) total UI components" -ForegroundColor White
Write-Host "Keeping $($usedComponents.Count) used components" -ForegroundColor Green
Write-Host ""

# Calculate unused components
$unusedComponents = $allComponents | Where-Object { $usedComponents -notcontains $_ }

Write-Host "Unused components to remove: $($unusedComponents.Count)" -ForegroundColor Yellow
Write-Host ""

if ($unusedComponents.Count -eq 0) {
    Write-Host "No unused components found. Your project is already clean!" -ForegroundColor Green
    exit 0
}

# Display list of components to be removed
Write-Host "The following components will be DELETED:" -ForegroundColor Yellow
foreach ($component in $unusedComponents) {
    Write-Host "  - $component" -ForegroundColor Red
}
Write-Host ""

# Ask for confirmation
$confirmation = Read-Host "Do you want to proceed? This action CANNOT be undone! (yes/no)"

if ($confirmation -ne "yes") {
    Write-Host "Operation cancelled by user." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Deleting unused components..." -ForegroundColor Cyan

# Delete unused components
$deletedCount = 0
$failedCount = 0

foreach ($component in $unusedComponents) {
    $filePath = Join-Path $uiComponentsPath $component
    try {
        Remove-Item -Path $filePath -Force
        Write-Host "[DELETED] $component" -ForegroundColor Green
        $deletedCount++
    }
    catch {
        Write-Host "[FAILED] Could not delete $component - $($_.Exception.Message)" -ForegroundColor Red
        $failedCount++
    }
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Cleanup Summary" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Successfully deleted: $deletedCount files" -ForegroundColor Green
Write-Host "Failed to delete: $failedCount files" -ForegroundColor Red
Write-Host "Remaining components: $($usedComponents.Count)" -ForegroundColor White
Write-Host ""

# Calculate space saved (approximate)
$estimatedSaved = $deletedCount * 2 # Rough estimate: 2KB per component
Write-Host "Estimated space saved: ~$estimatedSaved KB" -ForegroundColor Cyan
Write-Host ""

# Suggest next steps
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Run 'npm run build' to verify the build still works" -ForegroundColor White
Write-Host "2. Test your application to ensure nothing broke" -ForegroundColor White
Write-Host "3. Commit changes: git add . && git commit -m 'Remove unused UI components'" -ForegroundColor White
Write-Host "4. Push to deploy: git push" -ForegroundColor White
Write-Host ""

# Create a backup list file
$backupFile = "deleted-components-$(Get-Date -Format 'yyyyMMdd-HHmmss').txt"
$unusedComponents | Out-File -FilePath $backupFile
Write-Host "Backup list saved to: $backupFile" -ForegroundColor Cyan
Write-Host "Keep this file in case you need to restore any components later." -ForegroundColor Yellow
