# Rule for Creating New Rules

- **Author**: Tohar Laufer
- **Date**: 06/06/2025
- **Version**: 1.0.0
- **Priority**: High

## Description  
When the user requests to create a new rule (whether it's a new agent rule, coding rule, or a general rule), the rule must be created under the directory `.roo/rules/` with an indicative filename (e.g., `<indicative_rule_name>.md`). This `.roo` directory must be located at the project's root, not within any subdirectories like `src` or `app`.

If appropriate, rules should be organized into subfolders within `rules/` such as `rules/conventions/`, `rules/agent-workflow/`, etc.  

Rules **must not** be created outside of the `.roo/rules/` directory or in any other file format than Markdown (`.md`).

If the requested rule already exists, the user must be informed. Ask if they want to:  
- Add to or improve the existing rule, or
- Create another rule with different name and content, or
- Cancel the creation since the rule already exists.  

Rules should be clear, logical, well-formatted in Markdown, concise, and avoid unnecessary boilerplate to prevent context bloat.

Rules should always be created according to these instruction and according to the 'New Rule Template' described below. Even when edditing or changing rule, it should always follow those instructions and template.

## When to apply  
- Whenever the user requests creation of any new rule (agent, coding, or general).  
- When deciding where to save the rule and in what format.  
- When a rule with similar name or content already exists.

## When not to apply  
- When the user is not requesting a new rule creation.  
- When the user ask to create new mode, state, or personality (roo modes for example).
- When creating other types of files unrelated to rules.

## Example: New Rule Template

```md
# <Rule Title>

- **Author**: <Author Name>
- **Date**: <DD/MM/YYYY>
- **Version**: <1.0.0>
- **Priority**: <High/Medium/Low>

## Description
<Brief description of the rule’s purpose and scope.>

## When to apply
<Conditions or situations when this rule should be applied.>

## When not to apply
<Conditions or situations when this rule should be skipped or ignored.>

## Example <optional>
<When really helpful, an exmpale of situation the rule is applied or not applied, or to its result>
