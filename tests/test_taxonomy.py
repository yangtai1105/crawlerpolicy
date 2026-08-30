import pytest

from pipeline.taxonomy import FRONT_TRACKS, Front, Track, validate_tracks


def test_every_track_belongs_to_exactly_one_public_front():
    flattened = [track for tracks in FRONT_TRACKS.values() for track in tracks]

    assert set(FRONT_TRACKS) == set(Front)
    assert set(flattened) == set(Track)
    assert len(flattened) == len(set(flattened))


def test_validate_tracks_requires_primary_in_tracks():
    validate_tracks(
        Track.SEARCH_DISCOVERY,
        [Track.SEARCH_DISCOVERY, Track.CRAWLER_CONTROLS],
    )

    with pytest.raises(ValueError, match="primary_track must appear in tracks"):
        validate_tracks(Track.SEARCH_DISCOVERY, [Track.CRAWLER_CONTROLS])


def test_validate_tracks_rejects_empty_and_duplicate_tracks():
    with pytest.raises(ValueError, match="tracks must not be empty"):
        validate_tracks(Track.SEARCH_DISCOVERY, [])

    with pytest.raises(ValueError, match="tracks must not contain duplicates"):
        validate_tracks(
            Track.SEARCH_DISCOVERY,
            [Track.SEARCH_DISCOVERY, Track.SEARCH_DISCOVERY],
        )
