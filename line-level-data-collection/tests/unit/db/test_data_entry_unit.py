from line_level_data_collection.db.data_entry_record import DataEntryCount, ApprovalStatus


def test_to_response_json():
    entries = [
        DataEntryCount(label='bar', status=ApprovalStatus.REJECTED.name, count=1),
        DataEntryCount(label='foo', status=ApprovalStatus.UNPROCESSED.name, count=1),
        DataEntryCount(label='foo', status=ApprovalStatus.APPROVED.name, count=2),
        DataEntryCount(label='foo', status=ApprovalStatus.REJECTED.name, count=3)
    ]
    expected = [
        {
            'label': 'bar',
            'counts': [
                {
                    'status': ApprovalStatus.REJECTED.name,
                    'count': 1
                }
            ]
        },
        {
            'label': 'foo',
            'counts': [
                {
                    'status': ApprovalStatus.UNPROCESSED,
                    'count': 1
                },
                {
                    'status': ApprovalStatus.APPROVED,
                    'count': 2
                },
                {
                    'status': ApprovalStatus.REJECTED,
                    'count': 3
                }
            ]
        }
    ]
    assert DataEntryCount.to_response_json(entries)
