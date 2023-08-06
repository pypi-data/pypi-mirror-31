import * as React from 'react';
import { ProbeEvent } from '../model';
import { Event } from './event';


interface EventListProps {
    events: ProbeEvent[]
    onToggleEvent: (id: string) => any
}


export const EventList: React.SFC<EventListProps> = ({events, onToggleEvent}) => (
    <div>
        {(events || []).map(event =>
            <Event
                key={event.id}
                event={event}
                onToggleEvent={() => onToggleEvent(event.id)}
            />
        )}
    </div>
);
