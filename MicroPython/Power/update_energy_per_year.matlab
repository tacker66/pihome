%
% ThingSpeak MATLAB Analysis: update_energy_per_year.matlab
%

channelID   =  xxxxxxxx; 
readAPIKey  = 'xxxxxxxx'; 
writeAPIKey = 'xxxxxxxx'; 

test = 0;

energyFieldID = 2;
energyPerYearFieldID = 7;

firstEnergy = 0;
firstEnergyStart = datetime(2024,2,14,12,0,0);

offsetEnergy = 705
offsetEnergyStart = datetime(2025,5,22,12,0,0);

windowEnd   = datetime('now');
windowStart = windowEnd - hours(1);
if test
    fprintf(['last energy data interval: %s, %s\n'], windowStart, windowEnd); 
end

data = thingSpeakRead(channelID,'Fields',[energyFieldID],'DateRange',[windowStart,windowEnd],'ReadKey',readAPIKey);                                
data = rmmissing(data);
lastEnergy = 0;
if length(data) > 0
    lastEnergy = data(length(data));
end
if windowEnd > offsetEnergyStart
    lastEnergy = lastEnergy + offsetEnergy;
end
lastTimestamp = windowStart;
if test
    fprintf(['last energy data (len, val, time): %d, %d, %s\n'], length(data), lastEnergy, lastTimestamp); 
end

windowStart = lastTimestamp - years(1);
windowEnd   = windowStart + hours(1);
if test
    fprintf(['first energy data interval: %s, %s\n'], windowStart, windowEnd); 
end

data = thingSpeakRead(channelID,'Fields',[energyFieldID],'DateRange',[windowStart,windowEnd],'ReadKey',readAPIKey);                                
data = rmmissing(data);
if length(data) > 0
    firstEnergy = data(length(data))
    if windowEnd > offsetEnergyStart
        firstEnergy = firstEnergy + offsetEnergy;
    end
    avgEnergy = round(lastEnergy - firstEnergy, 2);
    if test
        fprintf(['len, first, last, avg: %d, %d, %d, %d\n'], length(data), firstEnergy, lastEnergy, avgEnergy);
    end
else
    duration = days(lastTimestamp - firstEnergyStart);
    avgEnergy = round(365.0 * (lastEnergy - firstEnergy) / duration, 2);
    if test
        fprintf(['len, first, last, avg, duration: %d, %d, %d, %d, %d\n'], length(data), firstEnergy, lastEnergy, avgEnergy, duration); 
    end
end

thingSpeakWrite(channelID, avgEnergy, 'Fields', [energyPerYearFieldID], 'WriteKey', writeAPIKey);
