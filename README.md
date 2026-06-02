# CFC Email HTML Archive

This repository stores ComForConnections email HTML files for webinars, podcasts, and related client campaign sends. It is intended as an internal/client-facing archive, not a public marketing site or application.

The goal is to keep past and active email HTML organized so campaign files can be found, reused, reviewed, or handed off without sorting through one large temporary folder.

## Repository Structure

```text
CFC-Email/
  Webinars/
    YYYY-MM-DD-Webinar/
      Constant-Contact-Webinar.html
      McKnights-Webinar.html
      Webinar.html

  Podcasts/
    US/
      [episode-number]-Podcast/
        Podcast.html
      [topic-slug]-Podcast/
        Podcast.html

    CA/
      [episode-number]-Podcast/
        Podcast.html
      [topic-slug]-Podcast/
        Podcast.html

  Surveys/
    YYYY-MM-DD-[topic]-Survey/
      Survey.html

  Source/
    Guidelines/
    Boilerplates/
```

## Folder Conventions

### Webinars

Webinar folders use the event date:

```text
Webinars/2026-08-13-Webinar/
```

Most webinars have two HTML versions for the same campaign content:

- `Constant-Contact-Webinar.html`
- `McKnights-Webinar.html`

These versions usually differ by UTM values, tracking links, or distribution partner. If there is only one version, use:

```text
Webinar.html
```

### Podcasts

Podcast folders are split by region because US and Canada episode numbers can overlap:

```text
Podcasts/US/
Podcasts/CA/
```

When an episode number is clear, use:

```text
Podcasts/US/34-Podcast/Podcast.html
Podcasts/CA/10-Podcast/Podcast.html
```

When the original HTML does not clearly identify an episode number, use a short topic slug:

```text
Podcasts/US/clinical-home-modifications-Podcast/Podcast.html
```

If more than one legacy HTML exists for the same podcast topic, keep both in the same folder with descriptive names.

### Surveys

Survey folders use the send or campaign date when known:

```text
Surveys/2024-12-13-Educational-Topics-Survey/Survey.html
```

## Active vs Archived Files

Most files in this repo are archived campaign HTML and are not actively in use. The current active webinar files should live in the appropriate dated webinar folder with the same naming conventions as above.

Before reusing an older file, review it as archived source material rather than production-ready HTML.

## Before Sending or Reusing HTML

Before any HTML file is sent, copied into a platform, or reused for a new campaign, check:

- Links and UTM values point to the correct campaign, partner, and destination.
- Image URLs still load and use the intended assets.
- Webinar dates, times, speaker names, and CE language are current.
- The send platform will provide required unsubscribe, preference, and address footer content.
- Any copied legacy markup is cleaned up for the current send.

## Source Materials

New campaign source material lives in [Source](Source). Use these files when starting a new send:

- [McKnights guidelines](Source/Guidelines/McKnights.md)
- [Boilerplate templates](Source/Boilerplates)

The source templates are intentionally generic and use `{{PLACEHOLDER}}` markers for campaign-specific links, images, and copy.

## Notes

This archive includes older generated HTML with known markup issues, such as nested links, missing image alt text, unescaped URL query strings, and some malformed image tags. Those older files were preserved for historical reference. Treat them as starting points only if they need to be reused.
