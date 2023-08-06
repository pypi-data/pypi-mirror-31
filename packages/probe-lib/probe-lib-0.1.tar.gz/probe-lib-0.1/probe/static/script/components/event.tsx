import * as React from 'react';

import { ProbeEvent } from '../model';

import { Button } from './button';


interface EventProps {
    event: ProbeEvent
    onToggleEvent: () => any
}


export const Event: React.SFC<EventProps> = ({event, onToggleEvent}) => (
    <div className="event">
        <div className="synopsis">
            <span className="date">{ formatDate(event.datetime) }</span>
            { event.description.map((text: string, index: number) =>
                (index % 2)
                    ? <em key={index}>{text}{' '}</em>
                    : <span key={index}>{text}{' '}</span>
            )}
            <span className="icons">
                <Button
                    state={event.expanded}
                    onClick={onToggleEvent} />
            </span>
        </div>
        { event.expanded &&
            <pre>{ JSON.stringify(event, null, 2) }</pre>
        }
    </div>
);


function formatDate(date: Date) {
    function f(value: number, len: number = 2) {
        let text = value.toString();
        return '0000'.substring(0, len - text.length) + text;
    }

    return `${f(date.getFullYear(), 4)}-${f(date.getMonth() + 1)}-${f(date.getDate())} ${f(date.getHours())}:${f(date.getMinutes())}`;
}
