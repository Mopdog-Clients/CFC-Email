# McKnights Campaign Guidelines

These are working guidelines for ComForConnections McKnights campaign HTML based on the current archive and partner-send pattern. If McKnights provides an official requirements sheet, use that as the source of truth and update this file.

## File Naming

Use this filename for McKnights webinar variants:

```text
McKnights-Webinar.html
```

Place it in the matching dated webinar folder:

```text
Webinars/YYYY-MM-DD-Webinar/McKnights-Webinar.html
```

## Link And UTM Rules

- Use the McKnights-specific registration or destination URL.
- Do not reuse Constant Contact links in McKnights versions.
- Use the approved `utm_source` value for the campaign, typically `McKnights` unless the campaign brief says otherwise.
- Use absolute `https://` URLs for every link.
- Escape query-string ampersands in HTML attributes as `&amp;`.
- Check every repeated CTA location: hero image, panelist image, button, and footer/landing-page link.

## HTML Requirements

- Keep the email body width at 600px.
- Use table-based email layout with inline styles.
- Avoid JavaScript, forms, iframes, embedded video, image maps, and external scripts.
- Use hosted image URLs with absolute `https://` paths.
- Include meaningful `alt` text for content images.
- Use empty `alt=""` only for decorative divider images.
- Keep copy readable if images are blocked.
- Set a real `<title>`, `lang="en"`, and preheader text.

## Content Checklist

Before handoff, confirm:

- Webinar title, date, time, time zone, and CE language are correct.
- Speaker/panelist names and credentials match the approved copy.
- CTA text matches the destination, usually `Register Now`.
- Registration links point to the McKnights campaign destination.
- Images are final, hosted, and accessible.
- Footer/unsubscribe/address handling is confirmed with the send platform or partner.

## Handoff Checklist

Send or retain the following for a McKnights campaign:

- Final `McKnights-Webinar.html`.
- Subject line.
- Preheader text.
- Primary destination URL.
- Image asset list or hosted image URLs.
- Any partner-specific notes from the campaign brief.
