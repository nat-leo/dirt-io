import { promises as fs } from 'fs';
import * as path from 'path';

type AreaSymbolsIndex = Record<string, string[]>;

const DEFAULT_FILE = path.resolve(process.cwd(), 'area-symbols.json');

/**
 * Add area symbols (e.g. "CA011") into area-symbols.json.
 *
 * - Uses first two letters as key (e.g. "CA" → ["CA011", "CA689", ...])
 * - All values are unique (no duplicates)
 * - Each key's list is sorted ascending
 */
export async function updateAreaSymbolsFile(
  symbols: string[],
  filePath: string = DEFAULT_FILE,
): Promise<AreaSymbolsIndex> {
  let data: AreaSymbolsIndex = {};

  // 1. Read existing file if it exists
  try {
    const raw = await fs.readFile(filePath, 'utf8');
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed === 'object') {
      data = parsed as AreaSymbolsIndex;
    }
  } catch (err: any) {
    if (err.code !== 'ENOENT') {
      // Some other read/parse error – surface it
      throw err;
    }
    // ENOENT means file doesn't exist yet; start with empty object
  }

  // 2. Merge new symbols
  for (const symbol of symbols) {
    // Optional: enforce expected pattern "AA999"
    if (!/^[A-Z]{2}\d{3}$/.test(symbol)) {
      // Skip anything malformed; or you could throw instead
      continue;
    }

    const key = symbol.slice(0, 2); // e.g. "CA"

    if (!data[key]) {
      data[key] = [];
    }

    if (!data[key].includes(symbol)) {
      data[key].push(symbol);
    }
  }

  // 3. Sort each key's list ascending
  for (const key of Object.keys(data)) {
    data[key].sort(); // lexicographic, so "CA001" < "CA011" < "CA101"
  }

  // 4. Write back to disk (pretty-printed)
  await fs.writeFile(filePath, JSON.stringify(data, null, 2), 'utf8');

  return data;
}
