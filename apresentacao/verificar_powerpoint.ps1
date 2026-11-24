$ErrorActionPreference = 'Stop'
$presentationRoot = $PSScriptRoot
$deckPath = Join-Path $presentationRoot 'apresentacao_rufas_5min.pptx'
$pdfPath = Join-Path $presentationRoot 'apresentacao_rufas_5min.pdf'
$previewPath = Join-Path $presentationRoot 'previas'
$evidencePath = Join-Path $presentationRoot 'evidencias/verificacao_powerpoint.json'
$app = $null
$deck = $null
try {
    $app = New-Object -ComObject PowerPoint.Application
    $app.DisplayAlerts = 1
    $deck = $app.Presentations.Open($deckPath, -1, 0, 0)
    if ($deck.Slides.Count -ne 4) { throw 'Expected exactly four slides.' }
    $overflow = @()
    foreach ($slide in $deck.Slides) {
        foreach ($shape in $slide.Shapes) {
            if ($shape.HasTextFrame -eq -1 -and $shape.TextFrame.HasText -eq -1) {
                $available = $shape.Height - $shape.TextFrame.MarginTop - $shape.TextFrame.MarginBottom
                $actual = $shape.TextFrame.TextRange.BoundHeight
                if ($actual -gt ($available + 2)) {
                    $overflow += @{slide=$slide.SlideIndex; shape=$shape.Name; actual_height=$actual; available_height=$available}
                }
            }
        }
    }
    $deck.Export($previewPath, 'PNG', 1600, 900)
    $deck.SaveAs($pdfPath, 32)
    $report = @{application='Microsoft PowerPoint'; opened=$true; slides=$deck.Slides.Count;
        width_points=$deck.PageSetup.SlideWidth; height_points=$deck.PageSetup.SlideHeight;
        exported_pdf='apresentacao_rufas_5min.pdf'; exported_previews='previas'; text_overflow_candidates=$overflow}
    $report | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $evidencePath -Encoding UTF8
    $report | ConvertTo-Json -Depth 6
} finally {
    if ($null -ne $deck) { $deck.Close() }
    if ($null -ne $app) { $app.Quit() }
}
