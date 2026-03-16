This module extends the OCA ``account_asset_transfer`` module adding:

* A "Transferred" state on assets to track which assets have been transferred via the AUC (Assets Under Construction) transfer wizard.
* Fields ``transfer_move_id`` and ``date_transfer`` to link transferred assets to their transfer journal entry.
* Computed fields ``from_asset_ids`` and ``to_asset_ids`` to navigate between source and destination assets.
* A "Revert Transfer" wizard to undo AUC transfers, restoring assets to their original state.
* Protection against accidental deletion of transfer journal entries (CURS moves) when unposting depreciation lines.
