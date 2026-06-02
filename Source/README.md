# Source Materials

This folder contains working source material for building new ComForConnections campaign HTML.

The archived campaign folders preserve past sends. The files in this `Source/` folder are intended for creating new sends without copying old one-off HTML directly.

## Contents

```text
Source/
  Guidelines/
    McKnights.md

  Boilerplates/
    Webinar-Constant-Contact.html
    Webinar-McKnights.html
    Podcast-US.html
    Podcast-CA.html
    Survey.html
```

## How To Use

1. Copy the appropriate boilerplate into the new campaign folder.
2. Replace all `{{PLACEHOLDER}}` values.
3. Update links, UTM values, image URLs, alt text, subject line, and preheader.
4. Validate the HTML before handing it off or loading it into a send platform.
5. Keep active campaign files in the dated or episode-based folder structure described in the root README.

## Placeholder Format

Boilerplates use double-brace placeholders:

```text
{{WEBINAR_TITLE}}
{{CTA_URL}}
{{HEADER_IMAGE_URL}}
```

These placeholders are not processed automatically. They are markers for manual replacement before a campaign is sent.
