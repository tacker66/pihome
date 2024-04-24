%
% ThingSpeak MATLAB Analysis: update_energy_per_month.matlab
%

channelID   =  xxxxxxxx; 
readAPIKey  = 'xxxxxxxx'; 
writeAPIKey = 'xxxxxxxx'; 

test = 0;

energyFieldID = 2;
energyPerMonthFieldID = 6;

firstEnergy = 0;
firstEnergyStart = datetime(2024,2,14,12,0,0);

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
lastTimestamp = windowStart;
if test
    fprintf(['last energy data (len, val, time): %d, %d, %s\n'], length(data), lastEnergy, lastTimestamp); 
end

windowStart = lastTimestamp - days(30);
windowEnd   = windowStart + hours(1);
if test
    fprintf(['first energy data interval: %s, %s\n'], windowStart, windowEnd); 
end

data = thingSpeakRead(channelID,'Fields',[energyFieldID],'DateRange',[windowStart,windowEnd],'ReadKey',readAPIKey);                                
data = rmmissing(data);
if length(data) > 0
    firstEnergy = data(length(data));
    avgEnergy = int64(lastEnergy - firstEnergy);
    if test
        fprintf(['first/avg energy: %d, %d / %d\n'], firstEnergy, avgEnergy);
    end
else
    duration = days(lastTimestamp - firstEnergyStart);
    avgEnergy = int64(30.0 * (lastEnergy - firstEnergy) / duration);
    if test
        fprintf(['first/avg energy, duration: %d/%d, %s\n'], firstEnergy, avgEnergy, duration); 
    end
end

if test
    fprintf(['energy per month: %d\n'], avgEnergy); 
end
thingSpeakWrite(channelID, avgEnergy, 'Fields', [energyPerMonthFieldID], 'WriteKey', writeAPIKey);
