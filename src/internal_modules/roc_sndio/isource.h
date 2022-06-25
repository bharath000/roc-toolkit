/*
 * Copyright (c) 2017 Roc Streaming authors
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */

//! @file roc_sndio/isource.h
//! @brief Source interface.

#ifndef ROC_SNDIO_ISOURCE_H_
#define ROC_SNDIO_ISOURCE_H_

#include "roc_audio/ireader.h"
#include "roc_sndio/terminal.h"

namespace roc {
namespace sndio {

//! Source interface.
class ISource : public ITerminal, public audio::IReader {
public:
    virtual ~ISource();

    //! Source state.
    enum State {
        //! Source is running and active.
        //! It is producing some sound.
        Playing,

        //! Source is running but is inactive.
        //! It is producing silence. It may be safely paused.
        Idle,

        //! Source is paused.
        //! It's not producing anything.
        Paused
    };

    //! Get current source state.
    virtual State state() const = 0;

    //! Pause reading.
    virtual void pause() = 0;

    //! Resume paused reading.
    //! @returns
    //!  false if an error occured.
    virtual bool resume() = 0;

    //! Restart reading from the beginning.
    //! @remarks
    //!  If the reading is paused, it's automatically resumed.
    //! @returns
    //!  false if an error occured.
    virtual bool restart() = 0;
};

} // namespace sndio
} // namespace roc

#endif // ROC_SNDIO_ISOURCE_H_
