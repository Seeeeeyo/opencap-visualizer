/**
 * File parsing utilities for OpenCap Visualizer
 * Pure functions for parsing various file formats
 */

/**
 * Parse OpenSim .mot force file content
 * @param {string} content - File content as string
 * @returns {Object} Parsed force data
 */
export function parseForcesData(content) {
  const lines = content.split('\n');
  let headerEnded = false;
  let columnHeaders = [];
  const timeData = [];
  const forceData = {};

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();

    if (line === 'endheader') {
      headerEnded = true;
      continue;
    }

    if (!headerEnded) continue;

    if (columnHeaders.length === 0) {
      // This is the column headers line
      columnHeaders = line.split(/\s+/);

      // Initialize force data arrays for each column
      columnHeaders.forEach(header => {
        if (header !== 'time') {
          forceData[header] = [];
        }
      });
      continue;
    }

    // Parse data lines
    if (line.length > 0) {
      const values = line.split(/\s+/).map(val => parseFloat(val));
      if (values.length === columnHeaders.length) {
        timeData.push(values[0]); // First column is time

        // Store force data for each column
        for (let j = 1; j < columnHeaders.length; j++) {
          forceData[columnHeaders[j]].push(values[j]);
        }
      }
    }
  }

  // Map column names to standard format for compatibility
  const mappedForceData = mapForceColumns(forceData, columnHeaders);

  return {
    time: timeData,
    columns: columnHeaders,
    data: mappedForceData,
    originalData: forceData // Keep original data for reference
  };
}

/**
 * Map different column naming conventions to standard format
 * @param {Object} forceData - Original force data object
 * @param {Array<string>} columnHeaders - Column header names
 * @returns {Object} Mapped force data with standard column names
 */
export function mapForceColumns(forceData, columnHeaders) {
  const mappedData = { ...forceData };
  
  // Define mapping patterns for different naming conventions
  const columnMappings = {
    // Pattern 1: R_ground_force_vx, L_ground_force_vx (current expected format)
    'R_ground_force_vx': ['R_ground_force_vx', 'ground_force_right_vx', 'right_ground_force_vx'],
    'R_ground_force_vy': ['R_ground_force_vy', 'ground_force_right_vy', 'right_ground_force_vy'],
    'R_ground_force_vz': ['R_ground_force_vz', 'ground_force_right_vz', 'right_ground_force_vz'],
    'R_ground_force_px': ['R_ground_force_px', 'ground_force_right_px', 'right_ground_force_px'],
    'R_ground_force_py': ['R_ground_force_py', 'ground_force_right_py', 'right_ground_force_py'],
    'R_ground_force_pz': ['R_ground_force_pz', 'ground_force_right_pz', 'right_ground_force_pz'],
    
    'L_ground_force_vx': ['L_ground_force_vx', 'ground_force_left_vx', 'left_ground_force_vx'],
    'L_ground_force_vy': ['L_ground_force_vy', 'ground_force_left_vy', 'left_ground_force_vy'],
    'L_ground_force_vz': ['L_ground_force_vz', 'ground_force_left_vz', 'left_ground_force_vz'],
    'L_ground_force_px': ['L_ground_force_px', 'ground_force_left_px', 'left_ground_force_px'],
    'L_ground_force_py': ['L_ground_force_py', 'ground_force_left_py', 'left_ground_force_py'],
    'L_ground_force_pz': ['L_ground_force_pz', 'ground_force_left_pz', 'left_ground_force_pz'],
  };

  // Apply mappings
  Object.keys(columnMappings).forEach(standardName => {
    const possibleNames = columnMappings[standardName];
    
    // Find which column name exists in the data
    for (const possibleName of possibleNames) {
      if (forceData[possibleName]) {
        mappedData[standardName] = forceData[possibleName];
        console.log(`Mapped ${possibleName} to ${standardName}`);
        break;
      }
    }
  });

  // Log what columns were found and mapped
  console.log('Original columns:', columnHeaders);
  console.log('Mapped force data keys:', Object.keys(mappedData).filter(key => 
    key.includes('ground_force') || key.includes('force')
  ));
  
  // Debug: Check if mapping was successful
  const hasRightForces = mappedData.R_ground_force_vx && mappedData.R_ground_force_vy && mappedData.R_ground_force_vz;
  const hasLeftForces = mappedData.L_ground_force_vx && mappedData.L_ground_force_vy && mappedData.L_ground_force_vz;
  console.log('Mapping success check:', {
    hasRightForces,
    hasLeftForces,
    rightForceData: hasRightForces ? 'Mapped successfully' : 'Not found',
    leftForceData: hasLeftForces ? 'Mapped successfully' : 'Not found'
  });

  return mappedData;
}

/**
 * Convert units to meters
 * @param {number} value - Value to convert
 * @param {string} units - Source units (mm, cm, m, in, ft)
 * @returns {number} Value in meters
 */
function convertToMeters(value, units) {
  const normalizedUnits = units ? units.toLowerCase().trim() : '';
  
  switch (normalizedUnits) {
    case 'mm':
    case 'millimeters':
      return value / 1000;
    case 'cm':
    case 'centimeters':
      return value / 100;
    case 'm':
    case 'meters':
    case 'meter':
      return value;
    case 'in':
    case 'inches':
      return value * 0.0254;
    case 'ft':
    case 'feet':
      return value * 0.3048;
    default:
      // Default assumption: mm to meters (for backward compatibility)
      if (normalizedUnits && normalizedUnits !== '') {
        console.warn(`Unknown units "${units}" in TRC file, assuming millimeters`);
      }
      return value / 1000;
  }
}

/**
 * Parse TRC marker file content
 * @param {string} content - File content as string
 * @param {string} fileName - Name of the file (for logging)
 * @returns {Object} Parsed marker data
 */
export function parseTrcFile(content, fileName = 'markers.trc') {
  console.log('Parsing TRC file:', fileName);
  console.log('Content length:', content.length);
  console.log('First 500 characters:', content.substring(0, 500));
  
  const lines = content.trim().split('\n');
  console.log('Number of lines:', lines.length);
  console.log('First 5 lines:', lines.slice(0, 5));

  // Parse header information
  const header = {};
  let dataStartIndex = 0;

  // Find the header end and data start
  let headerNames = [];
  let headerValues = [];
  let markerNamesLineIndex = -1;
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i] ? lines[i].trim() : '';
    if (!line) continue;
    
    if (line.includes('DataRate') || line.includes('CameraRate') || line.includes('NumFrames') || line.includes('NumMarkers') || line.includes('Units')) {
      // This is the header names line
      headerNames = line.split('\t');
      // The next line should contain the values
      if (i + 1 < lines.length) {
        const valueLine = lines[i + 1] ? lines[i + 1].trim() : '';
        if (valueLine) {
          headerValues = valueLine.split('\t');
          
          // Create header object from names and values
          for (let j = 0; j < headerNames.length && j < headerValues.length; j++) {
            header[headerNames[j]] = headerValues[j];
          }
          console.log('Parsed header:', header);
        }
      }
    }

    // Check for column headers line (contains Frame# and Time)
    if (line.includes('Frame#') && line.includes('Time')) {
      // This is the marker names line, store it for later parsing
      markerNamesLineIndex = i;
      // Skip the coordinate labels line and find the actual data start
      for (let j = i + 1; j < lines.length; j++) {
        const dataLine = lines[j] ? lines[j].trim() : '';
        if (dataLine && /^\d+\s/.test(dataLine)) {  // Line starts with a number
          dataStartIndex = j;
          break;
        }
      }
      break;
    }
  }

  // Parse column headers - find the marker names line (should contain Frame# and Time)
  if (markerNamesLineIndex === -1) {
    for (let i = 0; i < dataStartIndex; i++) {
      if (lines[i] && lines[i].includes('Frame#') && lines[i].includes('Time')) {
        markerNamesLineIndex = i;
        break;
      }
    }
  }

  if (markerNamesLineIndex === -1) {
    throw new Error('Could not find marker names line (Frame# and Time) in TRC file');
  }

  const headerLine = lines[markerNamesLineIndex];
  if (!headerLine) {
    throw new Error('Header line is undefined');
  }
  
  const columnHeaders = headerLine.split('\t');

  // Extract marker names by finding non-empty columns after Frame# and Time
  const markerNames = [];
  for (let i = 2; i < columnHeaders.length; i++) {
    const headerName = columnHeaders[i];
    if (headerName && headerName.trim()) {
      // Remove coordinate suffixes like :X, :Y, :Z
      const markerName = headerName.replace(/:.*$/, '').trim();
      if (markerName && markerNames.indexOf(markerName) === -1) {
        markerNames.push(markerName);
      }
    }
  }

  // Parse data rows
  const frameData = [];
  const timeData = [];
  const markerData = {};

  // Initialize marker data arrays
  markerNames.forEach(name => {
    markerData[name] = {
      x: [], y: [], z: []
    };
  });

  // Parse each data row
  for (let i = dataStartIndex; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;

    const values = line.split('\t');
    if (values.length < 2) continue;

    const frame = parseInt(values[0]);
    const time = parseFloat(values[1]);

    frameData.push(frame);
    timeData.push(time);

    // Parse marker positions (every 3 values after frame and time)
    let markerIndex = 0;
    for (let j = 2; j < values.length && markerIndex < markerNames.length; j += 3) {
      const markerName = markerNames[markerIndex];
      const x = parseFloat(values[j]) || 0;
      const y = parseFloat(values[j + 1]) || 0;
      const z = parseFloat(values[j + 2]) || 0;

      // Apply unit conversion based on header units
      const units = header.Units || '';
      const xConverted = convertToMeters(x, units);
      const yConverted = convertToMeters(y, units);
      const zConverted = convertToMeters(z, units);

      markerData[markerName].x.push(xConverted);
      markerData[markerName].y.push(yConverted);
      markerData[markerName].z.push(zConverted);

      markerIndex++;
    }
  }

  // Store the parsed data
  const parsedData = {
    header: header,
    markers: markerNames,
    frames: frameData,
    times: timeData,
    data: markerData,
    fileName: fileName
  };

  // Debug: Log the first few marker positions to verify parsing
  console.log('TRC File parsing debug:');
  console.log('Header units:', header.Units);
  console.log('Number of markers:', markerNames.length);
  console.log('Number of frames:', frameData.length);
  if (markerNames.length > 0) {
    const firstMarker = markerNames[0];
    console.log(`First marker "${firstMarker}" positions:`, {
      x: markerData[firstMarker].x.slice(0, 5),
      y: markerData[firstMarker].y.slice(0, 5),
      z: markerData[firstMarker].z.slice(0, 5)
    });
    
    // Also log a few more markers to see the range
    console.log('Sample marker positions (first 3 markers, first 3 frames):');
    for (let i = 0; i < Math.min(3, markerNames.length); i++) {
      const marker = markerNames[i];
      console.log(`${marker}:`, {
        x: markerData[marker].x.slice(0, 3),
        y: markerData[marker].y.slice(0, 3),
        z: markerData[marker].z.slice(0, 3)
      });
    }
  }

  return parsedData;
}

/**
 * Check if a .mot file is a force file based on filename and content
 * @param {File} file - File object to check
 * @returns {Promise<boolean>} True if file appears to be a force file
 */
export async function isForceMotFile(file) {
  const fileName = file.name.toLowerCase();
  console.log(`Checking if ${file.name} is a force file...`);
  
  // First check: filename contains "force"
  if (fileName.includes('force')) {
    console.log(`${file.name} identified as force file by filename`);
    return true;
  }
  
  // Second check: examine file content for force-related column headers
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target.result;
      const lines = content.split('\n');
      let headerEnded = false;
      let columnHeaders = [];
      
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        
        if (line === 'endheader') {
          headerEnded = true;
          continue;
        }
        
        if (!headerEnded) continue;
        
        if (columnHeaders.length === 0) {
          columnHeaders = line.split(/\s+/);
          
          // Check if any column headers contain force-related keywords
          const hasForceColumns = columnHeaders.some(header => {
            const lowerHeader = header.toLowerCase();
            return lowerHeader.includes('ground_force') || 
                   lowerHeader.includes('force') ||
                   lowerHeader.includes('cop') ||
                   (lowerHeader.includes('_vx') || lowerHeader.includes('_vy') || lowerHeader.includes('_vz'));
          });
          
          if (hasForceColumns) {
            console.log(`${file.name} identified as force file by column headers`);
            resolve(true);
            return;
          }
          
          // If no force columns found, it's likely a motion file
          console.log(`${file.name} identified as motion file (no force columns found)`);
          resolve(false);
          return;
        }
      }
      
      // If we couldn't determine, default to false (motion file)
      console.log(`${file.name} could not be determined, defaulting to motion file`);
      resolve(false);
    };
    
    reader.onerror = () => {
      console.error(`Error reading file ${file.name}`);
      resolve(false);
    };
    
    reader.readAsText(file);
  });
}

/**
 * Categorize .mot files as motion or force files
 * @param {Array<File>} motFiles - Array of .mot file objects
 * @returns {Promise<Object>} Object with motionFiles and forceFiles arrays
 */
export async function categorizeMotFiles(motFiles) {
  const motionFiles = [];
  const forceFiles = [];
  
  for (const file of motFiles) {
    const isForceFile = await isForceMotFile(file);
    if (isForceFile) {
      forceFiles.push(file);
    } else {
      motionFiles.push(file);
    }
  }
  
  return { motionFiles, forceFiles };
}
