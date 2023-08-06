import * as React from 'react';


interface FilterInputProps {
    value: string,
    onChange: (value: string) => any
}

export const FilterInput: React.SFC<FilterInputProps> = ({value, onChange}) => (
    <input
        type="text"
        className="mainfilter"
        autoFocus={true}
        value={value}
        onChange={evt => onChange(evt.target.value)} />
);
