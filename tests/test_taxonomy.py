import pytest

from pipeline.taxonomy import (
    FRONT_TRACKS,
    TRACK_ALIASES,
    Front,
    Subject,
    Track,
    resolve_track,
    validate_tracks,
)


def test_every_track_belongs_to_exactly_one_public_front():
    flattened = [track for tracks in FRONT_TRACKS.values() for track in tracks]

    assert set(FRONT_TRACKS) == set(Front)
    assert set(flattened) == set(Track)
    assert len(flattened) == len(set(flattened))


def test_validate_tracks_requires_primary_in_tracks():
    validate_tracks(
        Track.SEARCH_DISCOVERY,
        [Track.SEARCH_DISCOVERY, Track.ACCESS_CONTROLS],
    )

    with pytest.raises(ValueError, match="primary_track must appear in tracks"):
        validate_tracks(Track.SEARCH_DISCOVERY, [Track.ACCESS_CONTROLS])


def test_validate_tracks_rejects_empty_and_duplicate_tracks():
    with pytest.raises(ValueError, match="tracks must not be empty"):
        validate_tracks(Track.SEARCH_DISCOVERY, [])

    with pytest.raises(ValueError, match="tracks must not contain duplicates"):
        validate_tracks(
            Track.SEARCH_DISCOVERY,
            [Track.SEARCH_DISCOVERY, Track.SEARCH_DISCOVERY],
        )


def test_resolve_track_accepts_canonical_slugs():
    assert resolve_track("access-controls") is Track.ACCESS_CONTROLS
    assert resolve_track("platform-ecosystem") is Track.PLATFORM_ECOSYSTEM
    assert resolve_track("identity-authorization") is Track.IDENTITY_AUTHORIZATION


def test_resolve_track_resolves_pre_october_2026_slugs():
    assert resolve_track("crawler-controls") is Track.ACCESS_CONTROLS
    assert resolve_track("agentic-web") is Track.PLATFORM_ECOSYSTEM
    assert set(TRACK_ALIASES) == {"crawler-controls", "agentic-web"}


def test_resolve_track_rejects_unknown_slugs():
    with pytest.raises(ValueError):
        resolve_track("not-a-track")


def test_track_slugs_carry_no_subject_words():
    for track in Track:
        assert "crawler" not in track.value
        assert "agent" not in track.value


def test_identity_authorization_rolls_up_to_agents_identity():
    assert Track.IDENTITY_AUTHORIZATION in FRONT_TRACKS[Front.AGENTS_IDENTITY]


def test_subject_axis_values():
    assert [subject.value for subject in Subject] == ["crawler", "agent", "both", "unknown"]
