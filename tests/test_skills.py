import pytest
from app.skills import import_external_skill, SkillImportError


@pytest.mark.asyncio
async def test_skill_name_validation():
    with pytest.raises(SkillImportError):
        await import_external_skill(
            "https://raw.githubusercontent.com/owner/repo@0123456789012345678901234567890123456789/SKILL.md",
            "Bad Name",
        )


@pytest.mark.asyncio
async def test_skill_host_and_branch_controls():
    with pytest.raises(SkillImportError):
        await import_external_skill(
            "http://raw.githubusercontent.com/owner/repo/main/SKILL.md", "valid-name"
        )
    with pytest.raises(SkillImportError):
        await import_external_skill(
            "https://raw.githubusercontent.com/owner/repo/main/SKILL.md", "valid-name"
        )
