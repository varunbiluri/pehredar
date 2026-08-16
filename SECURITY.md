# Security policy

Pehredar handles call metadata and contacts, so privacy and safe failure are
security properties, not optional features.

## Supported versions

| Version | Supported |
| --- | --- |
| Latest GitHub beta | Yes |
| Older betas and alphas | No |
| Parked desktop voice research | Best effort |

## Report a vulnerability

Use GitHub's **Report a vulnerability** button on the repository Security page.
This creates a private security advisory. Do not file a public issue, attach
real user data, or test against a device/account you do not own or have explicit
permission to use.

Include affected version/commit, impact, reproduction steps using synthetic
data, and any suggested mitigation. Maintainers aim to acknowledge reports
within 72 hours, provide an initial assessment within seven days, and coordinate
disclosure after a fix is available. Timelines may change with complexity.

## Scope priorities

- Unauthorized exposure of contacts or phone numbers
- Unexpected network transmission
- Permission escalation or unsafe exported components
- Bypassing the fail-open policy in a way that suppresses legitimate calls
- Release-signing or update integrity problems
- Malicious or compromised dependencies

Social engineering, unsupported Android versions, and vulnerabilities in an
unmodified third-party model/runtime should generally be reported upstream.

## Safe harbor

Good-faith research that respects privacy, avoids disruption and data access,
and follows this policy will be treated as authorized security research. Stop
and report immediately if you encounter real personal data.
