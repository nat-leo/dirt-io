/**
 * Definitions.ts
 * 
 * This is where all the data type are defined. When anything at all is returned 
 * from the API/Service layer, it's going to be plopped inside one of these types. 
 * 
 */


export type Invoice = {
  id: string;
  customer_id: string;
  amount: number;
  date: string;
  // In TypeScript, this is called a string union type.
  // It means that the "status" property can only be one of the two strings: 'pending' or 'paid'.
  status: 'pending' | 'paid';
};

